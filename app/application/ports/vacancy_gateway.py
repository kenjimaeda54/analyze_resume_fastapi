from abc import ABC, abstractmethod

from app.domain.entities.vacancy import Vacancy


class VacancyGatewayInterface(ABC):

    @abstractmethod
    def create_vacancy(self,vacancy: Vacancy):
        pass

    @abstractmethod
    def get_vacancy(self,vacancy_id: int ) -> Vacancy:
        pass

    @abstractmethod
    def get_by_vacancy_public_id(self,public_id:  str ) -> Vacancy:
        pass

