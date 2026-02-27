"""
Service-level exceptions for OCR/Parser pipeline.
"""


class ReceiptProcessingError(ValueError):
    """User-facing receipt processing error with machine-readable code."""

    def __init__(self, detail: str, error_code: str):
        super().__init__(detail)
        self.detail = detail
        self.error_code = error_code
