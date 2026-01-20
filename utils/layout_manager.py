import numpy as np
from utils.exceptions import ProcessingError


class LayoutManager:

    DPI = 300
    A4_W = int((210 / 25.4) * DPI)
    A4_H = int((297 / 25.4) * DPI)

    @staticmethod
    def blank_a4():
        return (
            np.ones((LayoutManager.A4_H, LayoutManager.A4_W, 3), dtype=np.uint8) * 255
        )

    @staticmethod
    def center(image):
        try:
            canvas = LayoutManager.blank_a4()
            h, w, _ = image.shape
            y = (canvas.shape[0] - h) // 2
            x = (canvas.shape[1] - w) // 2
            canvas[y : y + h, x : x + w] = image
            return canvas
        except Exception as e:
            raise ProcessingError(f"Layout error: {e}")
