from pdf2image import convert_from_path
from utils.exceptions import ProcessingError


class PDFProcessor:

    @staticmethod
    def to_image(pdf_path):
        try:
            images = convert_from_path(pdf_path, dpi=300)
            return images[0]
        except Exception as e:
            raise ProcessingError(f"PDF error: {e}")
