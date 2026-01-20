import cv2
from utils.exceptions import ProcessingError


class ImageProcessor:

    @staticmethod
    def read(path):
        img = cv2.imread(path)
        if img is None:
            raise ProcessingError("Cannot read image")
        return img

    @staticmethod
    def face_crop(image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return image
            x, y, w, h = faces[0]
            return image[y : y + h, x : x + w]
        except Exception:
            return image

    @staticmethod
    def resize_mm(image, w_mm, h_mm, dpi=300):
        try:
            w_px = int((w_mm / 25.4) * dpi)
            h_px = int((h_mm / 25.4) * dpi)
            return cv2.resize(image, (w_px, h_px))
        except Exception as e:
            raise ProcessingError(f"Resize error: {e}")
