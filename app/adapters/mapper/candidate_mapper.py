from fastapi import UploadFile

from app.application.dto.request.create_candidate import CreateCandidate
from app.domain.entities.candidate import Candidate


class CandidateMapper:
    @staticmethod
    def to_domain(dto: CreateCandidate) -> Candidate:
        return  Candidate(
            cpf=dto.cpf,
            resume_path=dto.resume.filename or "",
            vacancy_id=dto.vacancy_id
        )