import json

from fastapi import UploadFile, File
from pydantic import BaseModel
from pydantic.v1 import Field


class CreateCandidate(BaseModel):
    cpf: str = Field(description="This filed is required", example="1234567890", min_length=4, max_length=4,)
    resume: UploadFile = Field(description="This filed is required")
    vacancy_id: int = Field(description="This filed is required")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cpf": "1234567890",
                "vacancy_id": 1,
            }
        }
    }
