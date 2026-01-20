import json
from core.document_base import DocumentBase
from utils.file_uploader import FileUploader
from utils.image_processor import ImageProcessor
from utils.layout_manager import LayoutManager


class AadhaarDocument(DocumentBase):

    def validate(self):
        FileUploader.validate(self.file_path)

    def process(self):
        with open("config/sizes.json") as f:
            sizes = json.load(f)

        img = ImageProcessor.read(self.file_path)
        size = sizes["aadhaar_full"]

        img = ImageProcessor.resize_mm(img, size["width_mm"], size["height_mm"])

        return LayoutManager.center(img)
