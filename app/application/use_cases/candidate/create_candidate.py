from app.application.ports.candidate_gateway import CandidateGatewayInterface
from app.domain.entities.candidate import Candidate


class CreateCandidateUseCase:
    def __init__(self, candidate_gateway: CandidateGatewayInterface):
        self.candidate_gateway = candidate_gateway


    def execute(self, candidate: Candidate):
         self.candidate_gateway.create_candidate(candidate)

    def __call__(self, candidate: Candidate):
        self.execute(candidate)


