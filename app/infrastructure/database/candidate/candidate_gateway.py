from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from app.application.ports.candidate_gateway import CandidateGatewayInterface
from app.domain.entities.candidate import Candidate
from app.domain.exception.candidate_exceptions import CandidateAlreadyExistsException
from app.infrastructure.database.models.candidate_model import CandidateTable


class CandidateDatabaseGateway(CandidateGatewayInterface):
    def __init__(self, db: Session):
        self.db = db

    def create_candidate(self, candidate: Candidate):
        candidate_table = CandidateTable(
            cpf=candidate.cpf,
            resume_path=candidate.resume_path,
            vacancy_id=candidate.vacancy_id,
            score=candidate.score or 0.0,
            status=candidate.status
        )
        try:
            self.db.add(candidate_table)
            self.db.commit()
            self.db.refresh(candidate_table)
        except IntegrityError:
            self.db.rollback()
            raise CandidateAlreadyExistsException(candidate=candidate)
        except Exception as e:
            self.db.rollback()
            raise e

