from pydantic import BaseModel,Field


class UpdateScoreRequest(BaseModel):
    score: float= Field(ge=0,le=100)
