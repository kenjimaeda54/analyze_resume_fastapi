from os import error

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.params import Depends
from starlette import status
from typing import Annotated

from pydantic import ValidationError

from app.adapters.mapper.candidate_mapper import CandidateMapper
from app.application.dto.request.create_candidate import CreateCandidate
from app.application.use_cases.candidate.create_candidate import CreateCandidateUseCase
from app.infrastructure.database.candidate.candidate_gateway import CandidateDatabaseGateway
from app.infrastructure.database.database import depends_db
from app.domain.exception.base import ErrorResponse
from app.adapters.messages.field_messages import build_field_error
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)

def candidate_use_case_gateway(db: depends_db):
    candidate_gateway_db = CandidateDatabaseGateway(db)
    return CreateCandidateUseCase(candidate_gateway_db)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_candidate(
    cpf: Annotated[str, Form()],
    resume: Annotated[UploadFile, File()],
    vacancy_id: Annotated[int, Form()],
    create_candidate_use_case: Annotated[CreateCandidateUseCase, Depends(candidate_use_case_gateway)]
):
    try:
        dto = CreateCandidate(cpf=cpf, vacancy_id=vacancy_id)
    except ValidationError as exception:
        fields = [build_field_error(err) for err in exception.errors()]
        error_response = ErrorResponse(
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="Invalid request data",
            fields=fields
        )
        return JSONResponse(
            status_code=error_response.http_status_code,
            content=error_response.model_dump(exclude_none=True),
        )

    candidate = CandidateMapper.to_domain(dto, resume_filename=resume.filename or "")
    create_candidate_use_case(candidate)
    return None