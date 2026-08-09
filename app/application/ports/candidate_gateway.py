from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.candidate import Candidate


class CandidateGatewayInterface(ABC):

    @abstractmethod
    def create_candidate(self, candidate: Candidate):
        pass

    @abstractmethod
    def get_candidate(self, cpf: str) -> Optional[Candidate]:
        pass
