from pydantic import BaseModel, Field


class CreateCandidate(BaseModel):
    cpf: str = Field(description="This field is required",max_length=11)
    vacancy_id: int = Field(description="This field is required")
    model_config = {
        "json_schema_extra": {
            "example": {
                "cpf": "1234567890",
                "vacancy_id": 1,
            }
        }
    }
