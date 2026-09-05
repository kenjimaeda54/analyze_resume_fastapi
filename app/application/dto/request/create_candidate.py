from pydantic import BaseModel, Field,EmailStr


class CreateCandidate(BaseModel):
    cpf: str = Field(description="This field is required",max_length=11)
    name: str = Field(description="This field is required")
    email : EmailStr = Field(description="This field is required")
    model_config = {
        "json_schema_extra": {
            "example": {
                "cpf": "1234567890",
                "name": "Joao Pedro",
                "email": "xxxx@gmail.com",
            }
        }
    }