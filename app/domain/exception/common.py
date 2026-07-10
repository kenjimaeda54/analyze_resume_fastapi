from typing import Optional

from pydantic import BaseModel


class FieldErrors(BaseModel):
    field: str
    message: str

class ErrorResponse(BaseModel):
    http_status_code: int
    error_code: str
    message: str
    fields: Optional[list[FieldErrors]] = None


class ConflictError(Exception):
    def __init__(self, message: str,error_code: str):
        super().__init__(message)
        self.error_code = error_code

class NotFoundError(Exception):
    def __init__(self, message: str,error_code: str):
        super().__init__(message)
        self.error_code = error_code
