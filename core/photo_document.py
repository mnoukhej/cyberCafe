import json
from core.document_base import DocumentBase
from utils.file_uploader import FileUploader
from utils.image_processor import ImageProcessor
from utils.layout_manager import LayoutManager


class PhotoDocument(DocumentBase):

    def __init__(self, file_path, photo_type):
        super().__init__(file_path)
        self.photo_type = photo_type

    def validate(self):
        FileUploader.validate(self.file_path)

    def process(self):
        with open("config/sizes.json") as f:
            sizes = json.load(f)

        img = ImageProcessor.read(self.file_path)
        img = ImageProcessor.face_crop(img)

        size = sizes[self.photo_type]
        img = ImageProcessor.resize_mm(img, size["width_mm"], size["height_mm"])

        return LayoutManager.center(img)
