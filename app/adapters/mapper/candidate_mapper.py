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
            resume_url="",
            email = dto.email,
        )

    @staticmethod
    def to_domain_from_table(table: CandidateTable) -> Candidate:
        return Candidate(
            id = table.id,
            public_id=str(table.public_id),
            cpf=table.cpf,
            name=table.name,
            resume_url=table.resume_url,
            email=table.email,
        )