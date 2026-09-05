from app.domain.exception.base import ResumeUrlError


class ResumeInvalidExtensionException(ResumeUrlError):
    def __init__(self):
        super().__init__(
            message="Invalid resume with this exstension",
            error_code="INVALID_RESUME_EXTENSION"
        )