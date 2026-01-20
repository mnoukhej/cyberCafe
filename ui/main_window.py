from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
)
import cv2
from core.photo_document import PhotoDocument
from utils.exceptions import CyberCafeError


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberCafe Printing Software")

        layout = QVBoxLayout()

        btn = QPushButton("Passport Photo Print")
        btn.clicked.connect(self.print_photo)

        layout.addWidget(btn)
        self.setLayout(layout)

    def print_photo(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Select Image")
            doc = PhotoDocument(path, "passport_photo")
            output = doc.safe_process()
            cv2.imwrite("temp/output.jpg", output)
            QMessageBox.information(self, "Success", "Preview created")
        except CyberCafeError as e:
            QMessageBox.critical(self, "Error", str(e))
