import os
from utils.exceptions import InvalidFileError


class FileUploader:

    ALLOWED = (".pdf", ".jpg", ".jpeg", ".png")

    @staticmethod
    def validate(path):
        if not path:
            raise InvalidFileError("No file selected")
        if not os.path.exists(path):
            raise InvalidFileError("File not found")
        if not path.lower().endswith(FileUploader.ALLOWED):
            raise InvalidFileError("Unsupported file type")
