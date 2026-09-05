from app.domain.exception.base import GeneralError, NotFoundError


class CandidateAlreadyExistsException(GeneralError):
    def __init__(self, field: str = "cpf"):
        super().__init__(
            message=f"Candidate  with  {field} already.",
            error_code="CANDIDATE_ALREADY_EXISTS"
        )

