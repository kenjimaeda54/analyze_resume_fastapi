from abc import abstractmethod, ABC
from typing import Optional

from app.domain.entities.application import Application
from app.domain.enum.candidate_status import CandidateStatus


class ApplicationGatewayInterface(ABC):

    @abstractmethod
    def get_many_application(self, vacancy_id: int, candidate_id: int) -> list[Application] | None:
        pass
    
    @abstractmethod
    def get_application_by_public_id(self,public_id: str) ->   Optional[Application]:
        pass

    @abstractmethod
    def update_score_application(self,score: float,public_id: str, status: CandidateStatus) -> None:
        pass
    

    @abstractmethod
    def create_application(self,application: Application) -> Application:
        pass

    @abstractmethod
    def find_by_candidate_and_vacancy(self, candidate_id: int, vacancy_id: int) -> Optional[Application]:
        pass