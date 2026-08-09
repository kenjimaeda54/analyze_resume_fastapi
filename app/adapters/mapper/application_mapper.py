from typing import List

from sqlalchemy import Sequence

from app.domain.entities.application import Application
from app.domain.entities.vacancy import Vacancy
from app.infrastructure.database.models.application_table import ApplicationTable


class ApplicationMapper:

    @staticmethod
    def to_domain_from_table(applications: Sequence[ApplicationTable]) -> List[Application]:
        return [
            Application(
                candidate_id=application.candidate_id,
                vacancy_id=application.vacancy_id,
                score=application.score,
                status=application.status,
                public_id=application.public_id,
            )
            for application in applications
        ]

    @staticmethod
    def  to_table_from_domain(application_table: ApplicationTable) -> Application:
         return Application(
             candidate_id=application_table.candidate_id,
             vacancy_id=application_table.vacancy_id,
             score=application_table.score,
             status=application_table.status,
             public_id=str(application_table.public_id),
         )
