from fastapi import APIRouter, UploadFile, File, Form
from fastapi.params import Depends, Path
from starlette import status
from typing import Annotated

from pydantic import ValidationError

from app.adapters.mapper.candidate_mapper import CandidateMapper
from app.application.dto.request.create_candidate import CreateCandidate
from app.application.dto.response.application_response_dto import ApplicationResponseDTO
from app.application.ports.application_gateway import ApplicationGatewayInterface
from app.application.use_cases.candidate import apply_to_vacancy_use_case
from app.application.use_cases.candidate.apply_to_vacancy_use_case import ApplyToVacancyUseCase
from app.infrastructure.database.gateway.application_gateway_implementation import ApplicationGatewayImplementation
from app.infrastructure.database.gateway.candidate_gateway_implementation import CandidateGatewayImplementation
from app.infrastructure.database.database import depends_db
from app.domain.exception.base import ErrorResponse
from app.adapters.messages.field_messages import build_field_error
from fastapi.responses import JSONResponse

from app.infrastructure.database.gateway.vacancy_gateway_implementation import VacancyGatewayImplementation

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)

def apply_candidate_use_case_gateway(db: depends_db):
    candidate_gateway = CandidateGatewayImplementation(db)
    application_gateway = ApplicationGatewayImplementation(db)
    vacancy_gateway = VacancyGatewayImplementation(db)
    return ApplyToVacancyUseCase(candidate_gateway=candidate_gateway, application_gateway=application_gateway, vacancy_gateway=vacancy_gateway)

#estamos enviando via form porque não aceita  no fastapi misturar json com File
#enviamos o resume que e um UploadFile
@router.post("/{vacancy_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_candidate_vacancy(
    cpf: Annotated[str, Form()],
    name: Annotated[str, Form()],
    resume: Annotated[UploadFile, File()],
    email: Annotated[str, Form()],
    vacancy_id:    Annotated[str,Path()],
    apply_vacancy_use_case: Annotated[ApplyToVacancyUseCase, Depends(apply_candidate_use_case_gateway)]
):
    try:
        dto = CreateCandidate(cpf=cpf, name=name,email=email)
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

    candidate = CandidateMapper.request_to_domain(dto, resume_filename=resume.filename or "")
    application = apply_vacancy_use_case(candidate=candidate, vacancy_id=vacancy_id)

    assert application.public_id is not None, "Application with publicId does not exist"

    return ApplicationResponseDTO(
       public_id=application.public_id,
        status=application.status,
    )