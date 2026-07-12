from app.application.dto.request.create_candidate import CreateCandidate
from app.domain.entities.candidate import Candidate


class CandidateMapper:
    @staticmethod
    def to_domain(dto: CreateCandidate, resume_filename: str = "") -> Candidate:
        # TODO: salvar arquivo resume em disco e passar o path real
        return Candidate(
            cpf=dto.cpf,
            resume_path=resume_filename,
            vacancy_id=dto.vacancy_id
        )