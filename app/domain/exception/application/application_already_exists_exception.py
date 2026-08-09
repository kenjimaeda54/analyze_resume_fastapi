from app.domain.exception.base import ConflictError


class ApplicationAlreadyExistsException(ConflictError):
    def __init__(self) -> None:
        super().__init__(
            message="This candidate is already registered for this position.",
            error_code="CANDIDATE_ALREADY_EXISTS_ON_VACANCY"
        )