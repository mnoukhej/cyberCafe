import win32print
import win32ui
from PIL import Image, ImageWin
from utils.exceptions import PrintingError


class PrintManager:

    @staticmethod
    def print_image(path):
        try:
            printer = win32print.GetDefaultPrinter()
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer)

            img = Image.open(path)
            dib = ImageWin.Dib(img)

            hdc.StartDoc("CyberCafe Print")
            hdc.StartPage()
            dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        except Exception as e:
            raise PrintingError(str(e))
