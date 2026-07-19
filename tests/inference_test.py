import commonforms
import commonforms.exceptions

import formalpdf
import pytest
from PIL import Image

from commonforms.inference import FFDNetDetector, promote_signature_widgets
from commonforms.utils import BoundingBox, Page, TextFragment, Widget


def test_inference(tmp_path):
    # tmp_path is a built-in pythest fixture where we'll write the outputs
    output_path = tmp_path / "output.pdf"
    commonforms.prepare_form("./tests/resources/input.pdf", output_path, model_or_path="FFDetr")

    assert output_path.exists()

    doc = formalpdf.open(output_path)
    assert len(doc[0].widgets()) > 0

    doc.document.close()


def test_inference_fast(tmp_path):
    output_path = tmp_path / "output.pdf"
    commonforms.prepare_form("./tests/resources/input.pdf", output_path, fast=True, model_or_path="FFDNet-L")

    assert output_path.exists()

    doc = formalpdf.open(output_path)
    assert len(doc[0].widgets()) > 0

    doc.document.close()


def test_mutlinline(tmp_path):
    output_path = tmp_path / "output.pdf"
    commonforms.prepare_form(
        "./tests/resources/input.pdf", output_path, fast=True, multiline=True
    )

    assert output_path.exists()

    doc = formalpdf.open(output_path)
    assert len(doc[0].widgets()) > 0

    doc.document.close()


def test_encrypted_failure(tmp_path):
    # Reminder to future Joe: password for encrypted PDF is "kanbanery"
    output_path = tmp_path / "output.pdf"

    with pytest.raises(commonforms.exceptions.EncryptedPdfError):
        commonforms.prepare_form("./tests/resources/encrypted.pdf", output_path)


def test_inference_ffdetr(tmp_path):
    # tmp_path is a built-in pythest fixture where we'll write the outputs
    output_path = tmp_path / "output.pdf"
    commonforms.prepare_form(
        "./tests/resources/input.pdf", output_path, model_or_path="FFDetr"
    )

    assert output_path.exists()

    doc = formalpdf.open(output_path)
    assert len(doc[0].widgets()) > 0

    doc.document.close()


def test_ffdnet_enables_class_agnostic_nms():
    class Model:
        def predict(self, source, **kwargs):
            assert len(source) == 1
            assert kwargs["agnostic_nms"] is True
            return []

    detector = FFDNetDetector.__new__(FFDNetDetector)
    detector.device = "cpu"
    detector.fast = False
    detector.model = Model()

    pages = [Page(image=Image.new("RGB", (1, 1)), width=1, height=1, text_fragments=[])]

    assert detector.extract_widgets(pages) == {}


def test_promote_signature_widgets_uses_signature_label_on_test_pdf():
    pages = [
        Page(
            image=Image.new("RGB", (1, 1)),
            width=1,
            height=1,
            text_fragments=[],
        ),
        Page(
            image=Image.new("RGB", (1, 1)),
            width=1,
            height=1,
            text_fragments=[
                TextFragment(
                    text="POLICYHOLDER/PATIENT SIGNATURE FAMILY RELATIONSHIP, IF NOT POLICYHOLDER DATE",
                    x0=0.37,
                    y0=0.61,
                )
            ],
        ),
    ]
    results = {
        1: [
            Widget(
                widget_type="TextBox",
                bounding_box=BoundingBox(x0=0.089, y0=0.857, x1=0.384, y1=0.895),
                page=1,
            ),
            Widget(
                widget_type="TextBox",
                bounding_box=BoundingBox(x0=0.752, y0=0.859, x1=0.927, y1=0.896),
                page=1,
            ),
        ]
    }

    promoted = promote_signature_widgets(pages, results)

    assert promoted[1][0].widget_type == "Signature"
    assert promoted[1][1].widget_type == "TextBox"


def test_promote_signature_widgets_skips_pages_without_signature_label():
    pages = [
        Page(
            image=Image.new("RGB", (1, 1)),
            width=1,
            height=1,
            text_fragments=[TextFragment(text="General contact information", x0=0.1, y0=0.2)],
        )
    ]
    results = {
        0: [
            Widget(
                widget_type="TextBox",
                bounding_box=BoundingBox(x0=0.1, y0=0.8, x1=0.3, y1=0.84),
                page=0,
            )
        ]
    }

    promoted = promote_signature_widgets(pages, results)

    assert promoted[0][0].widget_type == "TextBox"


# TODO(joe): future tests around handling encrypted PDFs
#   1. add a --password flag and test that inference doesn't fail
#   2. if a password is provided, ensure that the _output_ PDF remains encrpyted
#      with the same password
