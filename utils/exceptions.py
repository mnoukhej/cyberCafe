class CyberCafeError(Exception):
    pass


class InvalidFileError(CyberCafeError):
    pass


class ProcessingError(CyberCafeError):
    pass


class PrintingError(CyberCafeError):
    pass
