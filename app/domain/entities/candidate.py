from fastapi import UploadFile, File
from pydantic import BaseModel

from app.domain.enum.candidate_status import CandidateStatus


class Candidate(BaseModel):
    cpf: str
    resume_path: str
    vacancy_id: int
    score: float | None = None
    status:  CandidateStatus = CandidateStatus.PENDING
