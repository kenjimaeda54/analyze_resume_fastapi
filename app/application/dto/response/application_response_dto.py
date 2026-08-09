from pydantic import BaseModel, Field


class ApplicationResponseDTO(BaseModel):
    public_id: str = Field(description="Application ID")
    status: str = Field(description="Application status")
    model_config = {
        "json_schema_extra": {
            "example": {
                "public_id": "434224324",
                "status": "pending",
            }
        }
    }