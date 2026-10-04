from app.domain.exception.base import GeneralError


class CandidateException(GeneralError):
    def __init__(self, field: str = "cpf"):
        super().__init__(
            message=f"Something went wrong with the candidate {field}.",
            error_code="CANDIDATE_EXCEPTION"
        )