from pydantic import BaseModel

from app.domain.enum.candidate_status import CandidateStatus


class Candidate(BaseModel):
    public_id: str | None = None
    id: int | None = None
    cpf: str
    path_bucket: str
    name: str
    email: str
