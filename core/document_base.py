from abc import ABC, abstractmethod
from utils.exceptions import ProcessingError


class DocumentBase(ABC):

    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    def safe_process(self):
        try:
            self.validate()
            return self.process()
        except Exception as e:
            raise ProcessingError(str(e))
