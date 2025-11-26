from __future__ import annotations
from ultralytics import YOLO
from pathlib import Path
from huggingface_hub import hf_hub_download
from rfdetr import RFDETRNano, RFDETRBase, RFDETRMedium, RFDETRLarge

from commonforms.utils import BoundingBox, Page, Widget
from commonforms.form_creator import PyPdfFormCreator
from commonforms.exceptions import EncryptedPdfError

import formalpdf
import pypdfium2
import logging
import PIL


logging.basicConfig(level=logging.INFO)


# our mapping from (model_name_upper, fast) to (repo_id, filename) for the huggingface hub.
# keeping it simple and declarative like this becuase it's not like we're adding a bunch
# of models.
models = {
    ("FFDNET-S", True): ("jbarrow/FFDNet-S-cpu", "FFDNet-S.onnx"),
    ("FFDNET-S", False): ("jbarrow/FFDNet-S", "FFDNet-S.pt"),
    ("FFDNET-L", True): ("jbarrow/FFDNet-L-cpu", "FFDNet-L.onnx"),
    ("FFDNET-L", False): ("jbarrow/FFDNet-L", "FFDNet-L.pt"),
    ("FFDETR", False): ("jbarrow/FFDetr", "FFDetr.pth"),
}


def batch(lst: list, n: int = 8):
    l = len(lst)
    for ndx in range(0, l, n):
        yield lst[ndx : min(ndx + n, l)]


class FFDetrDetector:
    def __init__(self, model_or_path: str, device: int | str = "cpu") -> None:
        self.device = device
        self.model = RFDETRMedium(pretrain_weights=self.get_model_path(model_or_path))

        self.id_to_cls = {0: "TextBox", 1: "ChoiceButton", 2: "Signature"}

    def get_model_path(self, model_or_path: str) -> str:
        model_upper = model_or_path.upper()
        if model_upper in ["FFDETR"]:
            # download the model, will just use the cached version if it already exists
            repo_id, filename = models[(model_upper, False)]
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        else:
            model_path = model_or_path

        return model_path

    def resize(
        self,
        image: PIL.Image.Image,
        size: tuple[int, int] | int,
    ) -> PIL.Image.Image:
        if isinstance(size, int):
            size = (size, size)

        return image.resize(size, PIL.Image.Resampling.LANCZOS)

    def extract_widgets(
        self,
        pages: list[Page],
        confidence: float = 0.4,
        image_size: int = 1120,
        batch_size: int = 3,
    ) -> dict[int, list[Widget]]:
        image_size = 1024
        results = []
        for b in batch([self.resize(p.image, image_size) for p in pages], n=batch_size):
            predictions = self.model.predict(b, threshold=confidence)
            if len(pages) == 1 or batch_size == 1:
                predictions = [predictions]
            results.extend(predictions)

        widgets = {}

        for page_ix, detections in enumerate(results):
            logging.info(f"  Page {page_ix}: {len(detections)} fields detected")
            detections = detections.with_nms(threshold=0.1, class_agnostic=True)
            logging.info(f"\t\t{len(detections)} after nms")
            widgets[page_ix] = []

            for class_id, box in zip(detections.class_id, detections.xyxy):
                x0, x1 = box[[0, 2]] / pages[page_ix].image.width
                y0, y1 = box[[1, 3]] / pages[page_ix].image.height

                widget_type = self.id_to_cls[class_id]

                widgets[page_ix].append(
                    Widget(
                        widget_type=widget_type,
                        bounding_box=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
                        page=page_ix,
                    )
                )

            widgets[page_ix] = sort_widgets(widgets[page_ix])

        return widgets


class FFDNetDetector:
    def __init__(
        self, model_or_path: str, device: int | str = "cpu", fast: bool = False
    ) -> None:
        self.device = device
        self.fast = fast

        model_path = self.get_model_path(model_or_path, device, fast)
        self.model = YOLO(model_path, task="detect")

        self.id_to_cls = {0: "TextBox", 1: "ChoiceButton", 2: "Signature"}

    def get_model_path(
        self, model_or_path: str, device: int | str = "cpu", fast: bool = False
    ) -> str:
        """
        Construct the path to the model weights based on:
         (a) the requested model (in the package or external path)
         (b) --fast (if enabled, use ONNX, otherwise use pt)
        """
        model_upper = model_or_path.upper()
        if model_upper in ["FFDNET-S", "FFDNET-L"]:
            # download the model, will just use the cached version if it already exists
            repo_id, filename = models[(model_upper, fast)]
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        else:
            model_path = model_or_path

        return model_path

    def extract_widgets(
        self, pages: list[Page], confidence: float = 0.3, image_size: int = 1600
    ) -> dict[int, list[Widget]]:
        if self.fast:
            # overrides the image size to 1216, since that's all ONNX supports
            results = [
                self.model.predict(
                    p.image, iou=1, conf=confidence, augment=False, imgsz=1216
                )
                for p in pages
            ]
        else:
            results = self.model.predict(
                [p.image for p in pages],
                iou=0.1,
                conf=confidence,
                augment=True,
                imgsz=image_size,
                device=self.device,
            )

        widgets = {}
        for page_ix, result in enumerate(results):
            if isinstance(result, list):
                result = result[0]
            # no predictions, skip page
            if result is None or result.boxes is None:
                continue

            widgets[page_ix] = []
            for box in result.boxes.cpu().numpy():
                x, y, w, h = box.xywhn[0]
                cls_id = int(box.cls.item())
                widget_type = self.id_to_cls[cls_id]

                widgets[page_ix].append(
                    Widget(
                        widget_type=widget_type,
                        bounding_box=BoundingBox.from_yolo(cx=x, cy=y, w=w, h=h),
                        page=page_ix,
                    )
                )

            # do our best to sort the widgets into something resembling reading
            # order; this is important for being able to Tab/Shift-Tab back and
            # forth to navigate the page.
            widgets[page_ix] = sort_widgets(widgets[page_ix])

        return widgets


def sort_widgets(widgets: list[Widget]) -> list[Widget]:
    """
    Sort widgets in approximate reading order (left-to-right/top-to-bottom)
    which makes the LLMs less likely to mess up.
    """
    # Sort first by y coordinate, then x coordinate for reading order
    sorted_widgets = sorted(
        widgets,
        key=lambda w: (
            round(
                w.bounding_box.y0, 3
            ),  # Round to handle minor vertical alignment differences
            w.bounding_box.x0,
        ),
    )

    # Find rows of widgets by grouping those with similar y coordinates
    y_threshold = 0.01  # Threshold for considering widgets on same line
    lines = []
    current_line = []

    for widget in sorted_widgets:
        if (
            not current_line
            or abs(widget.bounding_box.y0 - current_line[0].bounding_box.y0)
            < y_threshold
        ):
            current_line.append(widget)
        else:
            # Sort widgets in line by x coordinate
            current_line.sort(key=lambda w: w.bounding_box.x0)
            lines.append(current_line)
            current_line = [widget]

    if current_line:
        current_line.sort(key=lambda w: w.bounding_box.x0)
        lines.append(current_line)

    # Flatten the lines back into single list
    return [widget for line in lines for widget in line]


def render_pdf(pdf_path: str) -> list[Page]:
    pages = []
    doc = formalpdf.open(pdf_path)
    try:
        for page in doc:
            image = page.render(dpi=144)
            pages.append(Page(image=image, width=image.width, height=image.height))
        return pages
    finally:
        doc.document.close()


def prepare_form(
    input_path: str | Path,
    output_path: str | Path,
    *,
    model_or_path: str = "FFDetr",
    keep_existing_fields: bool = False,
    use_signature_fields: bool = False,
    device: int | str = "cpu",
    image_size: int = 1024,
    confidence: float = 0.4,
    fast: bool = False,
    multiline: bool = False,
    batch_size: int = 4,
):
    if "FFDNET" in model_or_path.upper():
        detector = FFDNetDetector(model_or_path, device=device, fast=fast)
    else:
        detector = FFDetrDetector(model_or_path)

    try:
        pages = render_pdf(input_path)
    except pypdfium2._helpers.misc.PdfiumError:
        raise EncryptedPdfError

    results = detector.extract_widgets(
        pages, confidence=confidence, image_size=image_size
    )

    writer = PyPdfFormCreator(input_path)
    if not keep_existing_fields:
        writer.clear_existing_fields()

    for page_ix, widgets in results.items():
        for i, widget in enumerate(widgets):
            name = f"{widget.widget_type.lower()}_{widget.page}_{i}"

            if widget.widget_type == "TextBox":
                writer.add_text_box(
                    name, page_ix, widget.bounding_box, multiline=multiline
                )
            elif widget.widget_type == "ChoiceButton":
                writer.add_checkbox(name, page_ix, widget.bounding_box)
            elif widget.widget_type == "Signature":
                if use_signature_fields:
                    writer.add_signature(name, page_ix, widget.bounding_box)
                else:
                    writer.add_text_box(name, page_ix, widget.bounding_box)

    writer.save(output_path)
    writer.close()
