from app.domain.exception.base import GeneralError


class CandidateConflictException(GeneralError):
    def __init__(self):
        super().__init__(
            message=f"Conflict regarding the candidate CPF or email, please verify the  correct information to complete the registration.",
            error_code="CANDIDATE_CONCLIFCT_FIELDS"
        )