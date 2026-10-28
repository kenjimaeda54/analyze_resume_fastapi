from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.candidate import Candidate


class CandidateGatewayInterface(ABC):

    @abstractmethod
    def create_candidate(self, candidate: Candidate) -> Candidate:
        pass

    @abstractmethod
    def get_candidate(self, cpf: str,email: str) -> Optional[Candidate]:
        pass

    @abstractmethod
    def update_path_bucket(self, path_bucket: str, candidate_cpf: str) -> Candidate:
        pass
