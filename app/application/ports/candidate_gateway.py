from abc import ABC, abstractmethod

from app.domain.entities.candidate import Candidate


class CandidateGatewayInterface(ABC):

    @abstractmethod
    def create_candidate(self, request: Candidate):
        pass