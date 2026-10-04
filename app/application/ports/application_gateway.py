from abc import abstractmethod, ABC
from typing import Optional

from app.domain.entities.application import Application


class ApplicationGatewayInterface(ABC):

    @abstractmethod
    def get_application(self,vacancy_id: int,candidate_id: int) -> list[Application] | None:
        pass

    @abstractmethod
    def create_application(self,application: Application) -> Application:
        pass

    @abstractmethod
    def find_by_candidate_and_vacancy(self, candidate_id: int, vacancy_id: int) -> Optional[Application]:
        pass