from app.domain.exception.base import ConflictError, NotFoundError


class CandidateNotFound(NotFoundError):
    def __init__(self, cpf: str):
        super().__init__(
            error_code ="CANDIDATE_NOT_FOUND",
            message = f"Candidate with CPF {cpf} not found."
        )