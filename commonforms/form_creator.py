from pypdf import PdfReader, PdfWriter
from pypdf.annotations import AnnotationDictionary
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from commonforms.utils import BoundingBox


def rect_for(bounding_box: BoundingBox, page) -> ArrayObject:
    # because the PDFs are rendered to images with the CropBox, we need to use
    # that as the offset for where we insert the widgets
    page = page.cropbox if page.cropbox else page.mediabox
    # here I'm flipping the page.top/page.bottom to change from top-left origin
    # to bottom-right origin; this results in a negative height, but the math
    # works out in the end
    page_x0, page_y0, page_x1, page_y1 = (page.left, page.top, page.right, page.bottom)
    page_width = page_x1 - page_x0
    page_height = page_y1 - page_y0

    x0 = page_x0 + (bounding_box.x0 * page_width)
    y0 = page_y0 + (bounding_box.y1 * page_height)
    x1 = page_x0 + (bounding_box.x1 * page_width)
    y1 = page_y0 + (bounding_box.y0 * page_height)

    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0

    return ArrayObject(
        [
            NumberObject(x0),
            NumberObject(y0),
            NumberObject(x1),
            NumberObject(y1),
        ]
    )


class Textbox(AnnotationDictionary):
    def __init__(
        self,
        name: str,
        rect: ArrayObject,
        *,
        multiline: bool = False,
        value: str | None = None,
        default_value: str | None = None,
    ):
        super().__init__()

        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Tx"),
                NameObject("/T"): TextStringObject(name or ""),
                NameObject("/V"): TextStringObject(value or ""),
                NameObject("/DV"): TextStringObject(default_value or ""),
                NameObject("/Ff"): NumberObject(0 if not multiline else (1 << 12)),
                NameObject("/F"): NumberObject(4),
                NameObject("/Rect"): rect,
                NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 0 0 rg"),
            }
        )


class Checkbox(AnnotationDictionary):
    def __init__(
        self,
        name: str,
        rect: ArrayObject,
        *,
        multiline: bool = False,
        value: bool | None = None,
        default_value: str | None = None,
    ):
        super().__init__()
        pdf_value = NameObject("/Off") if not value else NameObject("/Yes")

        width = max(float(rect[2]) - float(rect[0]), 1)
        height = max(float(rect[3]) - float(rect[1]), 1)

        def appearance(checked: bool) -> DecodedStreamObject:
            stream = DecodedStreamObject()
            stream.update(
                {
                    NameObject("/Type"): NameObject("/XObject"),
                    NameObject("/Subtype"): NameObject("/Form"),
                    NameObject("/BBox"): ArrayObject(
                        [NumberObject(0), NumberObject(0), NumberObject(width), NumberObject(height)]
                    ),
                }
            )
            if checked:
                stream.set_data(
                    f"q 0 0 0 RG {min(width, height) * 0.12:.4f} w "
                    f"{width * 0.18:.4f} {height * 0.50:.4f} m "
                    f"{width * 0.43:.4f} {height * 0.23:.4f} l "
                    f"{width * 0.84:.4f} {height * 0.78:.4f} l S Q".encode()
                )
            else:
                stream.set_data(b"")
            return stream

        normal_appearance = DictionaryObject(
            {
                NameObject("/Off"): appearance(False),
                NameObject("/Yes"): appearance(True),
            }
        )

        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Btn"),
                NameObject("/Ff"): NumberObject(0),
                NameObject("/F"): NumberObject(4),
                NameObject("/Rect"): rect,
                NameObject("/V"): pdf_value,
                NameObject("/AS"): pdf_value,
                NameObject("/AP"): DictionaryObject(
                    {NameObject("/N"): normal_appearance}
                ),
                NameObject("/T"): TextStringObject(name),
            }
        )


class Signature(AnnotationDictionary):
    def __init__(self, name: str, rect: ArrayObject):
        super().__init__()
        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Sig"),
                NameObject("/T"): TextStringObject(name),
                NameObject("/Rect"): rect,
                NameObject("/F"): NumberObject(4),
            }
        )


class PyPdfFormCreator:
    def __init__(self, input_path: str):
        self.reader = PdfReader(input_path)
        # NOTE: Commenting out add_form_topname as it causes lazy loading issues with pages
        # self.reader.add_form_topname("original")
        self.writer = PdfWriter(clone_from=self.reader)
        # Keep reader open until we're done - pypdf uses lazy loading

        zapf_font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/ZapfDingbats"),
                NameObject("/Name"): NameObject("/ZaDb"),
            }
        )
        self.zapf_font = self.writer._add_object(zapf_font)

    def clear_existing_fields(self):
        """Clear all existing form fields from the PDF."""
        # Get the root form object if it exists
        if hasattr(self.writer, "_root_object"):
            root = self.writer._root_object
            if NameObject("/AcroForm") in root:
                acroform = root[NameObject("/AcroForm")]
                if NameObject("/Fields") in acroform:
                    # Replace with empty array to clear all fields
                    acroform[NameObject("/Fields")] = ArrayObject()

        # Also clear widget annotations from each page
        for i in range(len(self.writer.pages)):
            page = self.writer.pages[i]
            if NameObject("/Annots") in page:
                page[NameObject("/Annots")] = ArrayObject()

    def add_text_box(
        self,
        name: str,
        page: int,
        bounding_box: BoundingBox,
        multiline: bool = False,
    ) -> None:
        rect = rect_for(bounding_box, self.writer.pages[page])
        textbox = Textbox(name=name, rect=rect, multiline=multiline)
        self.writer.add_annotation(page_number=page, annotation=textbox)

    def add_checkbox(self, name: str, page: int, bounding_box: BoundingBox) -> None:
        rect = rect_for(bounding_box, self.writer.pages[page])
        checkbox = Checkbox(name=name, rect=rect)
        self.writer.add_annotation(page_number=page, annotation=checkbox)

    def add_signature(self, name: str, page: int, bounding_box: BoundingBox) -> None:
        rect = rect_for(bounding_box, self.writer.pages[page])
        signature = Signature(name=name, rect=rect)
        self.writer.add_annotation(page_number=page, annotation=signature)

    def save(self, output_path: str) -> None:
        self.writer.reattach_fields()
        with open(output_path, "wb") as fp:
            self.writer.write(fp)

    def close(self) -> None:
        self.writer.close()
        self.reader.close()
