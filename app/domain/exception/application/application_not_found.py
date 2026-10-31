from app.domain.exception.base import GeneralError


class ApplicationNotFound(GeneralError):
    def  __init__(self,public_id: str):
        super().__init__(
            message=f"This application with {public_id} not found on system",
            error_code="APPLICATION_NOT_FOUND"
        )