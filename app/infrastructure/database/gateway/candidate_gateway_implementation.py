from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from app.adapters.mapper.candidate_mapper import CandidateMapper
from app.application.ports.candidate_gateway import CandidateGatewayInterface
from app.domain.entities.candidate import Candidate
from app.domain.exception.candidate.candidate_exceptions import CandidateAlreadyExistsException
from app.domain.exception.candidate.candidate_not_found import CandidateNotFound
from app.infrastructure.database.models.candidate_table import CandidateTable


class CandidateGatewayImplementation(CandidateGatewayInterface):
    def __init__(self, db: Session):
        self.db = db

    def create_candidate(self, candidate: Candidate) -> Candidate:
        candidate_table = CandidateTable(
            cpf=candidate.cpf,
            resume_path=candidate.resume_path,
            name=candidate.name,
            email=candidate.email,
        )
        try:
            self.db.add(candidate_table)
            self.db.commit()
            self.db.refresh(candidate_table)
            #automaticamente o candidate_table e atribuido o id
            return  CandidateMapper.to_domain_from_table(candidate_table)
        except IntegrityError as e:
            self.db.rollback()
            raise CandidateAlreadyExistsException(candidate=candidate)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_candidate(self, cpf: str) -> Optional[Candidate]:
        try:
            statement = select(CandidateTable).where(CandidateTable.cpf == cpf)
            db_candidate: Optional[CandidateTable] = self.db.execute(statement).scalar_one_or_none()

            if db_candidate is None:
                return None

            return CandidateMapper.to_domain_from_table(db_candidate)
        except:
            raise CandidateNotFound(cpf=cpf)

    def delete_candidate(self, cpf: str):
        try:
            statement = select(CandidateTable).where(CandidateTable.cpf == cpf)
            db_candidate: Optional[CandidateTable] = self.db.execute(statement).scalar_one_or_none()

            if db_candidate is  None:
                raise CandidateNotFound(cpf=cpf)

            db_candidate.deleted_at = datetime.now()

            self.db.commit()
            self.db.refresh(db_candidate)

        except Exception as e:
            raise e
