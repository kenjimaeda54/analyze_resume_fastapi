from app.domain.entities.candidate import Candidate
from app.domain.exception.common import ConflictError, NotFoundError


class CandidateAlreadyExistsException(ConflictError):
    def __init__(self, candidate: Candidate):
        super().__init__(
            message=f"Candidate  with CPF {candidate.cpf} already.",
            error_code="CANDIDATE_ALREADY_EXISTS"
        )
