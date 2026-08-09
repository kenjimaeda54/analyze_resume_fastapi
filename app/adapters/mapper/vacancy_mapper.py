from app.domain.entities.vacancy import Vacancy
from app.infrastructure.database.models.vacancy_table import VacancyTable

class VacancyMapper:

    @staticmethod
    def to_domain_from_table(vacancy_table: VacancyTable) -> Vacancy:
        return Vacancy(
            id=vacancy_table.id,
            title=vacancy_table.title,
            description=vacancy_table.description,
            company=vacancy_table.company
        )