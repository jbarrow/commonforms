from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject

def enable_multiline_fields(input_pdf: str, output_pdf: str):
    """
    Enables multiline text input on all text fields in a fillable PDF.
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                if obj.get("/FT") == NameObject("/Tx"):
                    current_flags = obj.get("/Ff", NumberObject(0))
                    new_flags = int(current_flags) | 4096  # set multiline flag
                    obj.update({NameObject("/Ff"): NumberObject(new_flags)})
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"Done! Modified PDF saved as {output_pdf}")