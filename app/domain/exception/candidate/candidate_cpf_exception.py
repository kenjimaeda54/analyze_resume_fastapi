from app.domain.exception.base import GeneralError


class CandidateCpfException(GeneralError):
    def __init__(self):
        super().__init__(
            message = "CPF need be valid.",
            error_code = "NOT_EXISTS_CPF"
        )
