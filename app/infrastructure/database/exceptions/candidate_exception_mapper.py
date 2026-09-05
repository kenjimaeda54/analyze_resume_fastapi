from sqlalchemy.exc import IntegrityError

from app.domain.entities.candidate import Candidate
from app.domain.exception.candidate.candidate__already_exists_exceptions import CandidateAlreadyExistsException


def map_candidate_integrity_error(error: IntegrityError) -> CandidateAlreadyExistsException:
    error_message = str(error.orig)



    if "candidate_email_key" in error_message:
        return CandidateAlreadyExistsException(field="email")

    return CandidateAlreadyExistsException(field="cpf")


