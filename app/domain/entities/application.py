from pydantic import BaseModel

from app.domain.enum.candidate_status import CandidateStatus


class Application(BaseModel):
     public_id: str | None = None
     candidate_id: int
     vacancy_id: int
     score: float | None = None
     status: CandidateStatus = CandidateStatus.PENDING

