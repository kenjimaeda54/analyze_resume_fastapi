from app.domain.exception.base import GeneralError


class ApplicationAlreadyExistsException(GeneralError):
    def __init__(self) -> None:
        super().__init__(
            message="This candidate is already registered for this position(cpf or email registered)",
            error_code="CANDIDATE_ALREADY_EXISTS_ON_VACANCY"
        )