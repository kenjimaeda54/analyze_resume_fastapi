from app.application.dto.request.create_candidate import CreateCandidate
from app.domain.entities.candidate import Candidate
from app.infrastructure.database.models.candidate_table import CandidateTable


class CandidateMapper:
    @staticmethod
    def request_to_domain(dto: CreateCandidate) -> Candidate:
        # TODO: salvar arquivo resume em disco e passar o path real
        return Candidate(
            cpf=dto.cpf,
            name=dto.name,
            path_bucket="",
            email = dto.email,
        )

    @staticmethod
    def to_domain_from_table(table: CandidateTable) -> Candidate:
        return Candidate(
            id = table.id,
            public_id=str(table.public_id),
            cpf=table.cpf,
            name=table.name,
            path_bucket=table.path_bucket,
            email=table.email,
        )