from fastapi import APIRouter, UploadFile, File, Form
from fastapi.params import Depends
from starlette import status
from typing import Annotated

from app.adapters.mapper.candidate_mapper import CandidateMapper
from app.application.dto.request.create_candidate import CreateCandidate
from app.application.use_cases.candidate.create_candidate_usecase import CreateCandidateUseCase
from app.infrastructure.database.candidate.candidate_database_gateway import CandidateDatabaseGateway
from app.infrastructure.database.database import depends_db

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
    dto = CreateCandidate(cpf=cpf, vacancy_id=vacancy_id,resume=resume)
    candidate = CandidateMapper.to_domain(dto)
    create_candidate_use_case(candidate)
