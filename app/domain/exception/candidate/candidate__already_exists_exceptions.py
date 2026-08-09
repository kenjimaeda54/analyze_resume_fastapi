from app.domain.entities.candidate import Candidate
from app.domain.exception.base import ConflictError, NotFoundError


class CandidateAlreadyExistsException(ConflictError):
    def __init__(self, field: str = "cpf"):
        super().__init__(
            message=f"Candidate  with  {field} already.",
            error_code="CANDIDATE_ALREADY_EXISTS"
        )

