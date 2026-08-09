from app.domain.exception.base import NotFoundError


class VacancyNotFound(NotFoundError):
    def __init__(self, vacancy_id: int  | str) -> None:
         super().__init__(
             message=f"Vacancy with ID {vacancy_id} not found.",
             error_code="VACANCY_NOT_FOUND"
         )