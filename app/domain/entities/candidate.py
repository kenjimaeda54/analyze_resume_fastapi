from pydantic import BaseModel

from app.domain.enum.candidate_status import CandidateStatus


class Candidate(BaseModel):
    public_id: str | None = None
    id: int | None = None
    cpf: str
    resume_url: str
    name: str
    email: str
