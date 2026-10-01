from app.domain.exception.base import GeneralError


class CandidateException(GeneralError):
    def __init__(self, filed: str = "cpf"):
        super().__init__(
            message=f"Something went wrong with the candidate {filed}.",
            error_code="CANDIDATE_EXCEPTION"
        )