from datetime import datetime
from typing import Optional, Any

from sqlalchemy import select, Select
from sqlalchemy.orm import Session

from app.adapters.mapper.vacancy_mapper import VacancyMapper
from app.application.ports.vacancy_gateway import VacancyGatewayInterface
from app.domain.entities.vacancy import Vacancy
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound
from app.infrastructure.database.models.vacancy_table import VacancyTable


class VacancyGatewayImplementation(VacancyGatewayInterface):
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def _find_vacancy(self, statement: Select[tuple[Any]]) -> Optional[Vacancy]:
        vacancy_db: Optional[VacancyTable] = self.db_session.execute(statement).scalar_one_or_none()

        if vacancy_db is None:
            return None

        return VacancyMapper.to_domain_from_table(vacancy_db)

    def get_by_vacancy_public_id(self,public_id:  str ) -> Optional[Vacancy]:
        try:
            statement = select(VacancyTable).where(VacancyTable.public_id == public_id)

            return self._find_vacancy(statement)

        except Exception:
            raise VacancyNotFound(vacancy_id=public_id)

    def get_vacancy(self, vacancy_id: int) -> Optional[Vacancy]:
        try:
            statement = select(VacancyTable).where(VacancyTable.id == vacancy_id)

            return self._find_vacancy(statement)

        except Exception:
            raise VacancyNotFound(vacancy_id=vacancy_id)


    def create_vacancy(self, vacancy: Vacancy) -> None:
        try:
            vacancy_table = VacancyTable(
                title=vacancy.title,
                description=vacancy.description,
                company=vacancy.company,
            )
            self.db_session.add(vacancy_table)
            self.db_session.commit()
            self.db_session.refresh(vacancy_table)
        except Exception:
            self.db_session.rollback()
            raise


    def delete_vacancy(self, vacancy_id: int) -> None:
        try:
            statement = select(VacancyTable).where(VacancyTable.id == vacancy_id)
            vacancy_db: Optional[VacancyTable] = self.db_session.execute(statement).scalar_one_or_none()

            if vacancy_db is None:
                raise VacancyNotFound(vacancy_id=vacancy_id)

            vacancy_db.delete_at = datetime.now()

            self.db_session.commit()
            self.db_session.refresh(vacancy_db)

        except Exception as e:
            raise e


