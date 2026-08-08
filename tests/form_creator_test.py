from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, IndirectObject, NameObject

from commonforms.form_creator import PyPdfFormCreator
from commonforms.utils import BoundingBox


def test_checkbox_appearance_streams_are_indirect_and_flatten_checked_state(tmp_path):
    input_path = tmp_path / "blank.pdf"
    checkbox_path = tmp_path / "checkbox.pdf"
    flattened_path = tmp_path / "flattened.pdf"

    blank_writer = PdfWriter()
    blank_writer.add_blank_page(width=612, height=792)
    with input_path.open("wb") as output:
        blank_writer.write(output)
    blank_writer.close()

    creator = PyPdfFormCreator(input_path)
    creator.add_checkbox("agree", 0, BoundingBox(x0=0.1, y0=0.1, x1=0.2, y1=0.2))
    creator.save(checkbox_path)
    creator.close()

    checkbox_reader = PdfReader(checkbox_path)
    annotation = checkbox_reader.pages[0]["/Annots"][0].get_object()
    normal_appearances = annotation["/AP"]["/N"]

    for state in ("/Off", "/Yes"):
        appearance_reference = normal_appearances.raw_get(NameObject(state))
        assert isinstance(appearance_reference, IndirectObject)

        appearance = appearance_reference.get_object()
        assert appearance["/Type"] == "/XObject"
        assert appearance["/Subtype"] == "/Form"
        assert "/BBox" in appearance
        assert "/Resources" in appearance

    # pypdf versions can preserve insignificant PDF whitespace in empty streams.
    assert normal_appearances["/Off"].get_data().strip() == b""
    checked_appearance = normal_appearances["/Yes"]
    checked_bbox = list(checked_appearance["/BBox"])
    checked_resources = dict(checked_appearance["/Resources"])
    checked_data = checked_appearance.get_data()
    assert checked_data

    flatten_writer = PdfWriter(clone_from=checkbox_reader)
    flatten_writer.update_page_form_field_values(
        None, {"agree": "/Yes"}, auto_regenerate=False, flatten=True
    )
    with flattened_path.open("wb") as output:
        flatten_writer.write(output)
    flatten_writer.close()
    checkbox_reader.close()

    flattened_reader = PdfReader(flattened_path)
    flattened_page = flattened_reader.pages[0]
    operations = ContentStream(
        flattened_page.get_contents(), flattened_reader
    ).operations
    do_operations = [operands for operands, operator in operations if operator == b"Do"]

    assert len(do_operations) == 1
    xobject_name = do_operations[0][0]
    flattened_appearance = (
        flattened_page["/Resources"]["/XObject"].raw_get(xobject_name).get_object()
    )

    assert flattened_appearance["/Type"] == "/XObject"
    assert flattened_appearance["/Subtype"] == "/Form"
    assert list(flattened_appearance["/BBox"]) == checked_bbox
    assert dict(flattened_appearance["/Resources"]) == checked_resources
    assert flattened_appearance.get_data() == checked_data
    flattened_reader.close()
