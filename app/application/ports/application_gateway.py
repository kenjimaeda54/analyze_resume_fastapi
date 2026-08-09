from abc import abstractmethod, ABC

from app.domain.entities.application import Application


class ApplicationGatewayInterface(ABC):

    @abstractmethod
    def get_application(self,vacancy_id: int,candidate_id: int) -> Application:
        pass

    @abstractmethod
    def create_application(self,application: Application) -> Application:
        pass