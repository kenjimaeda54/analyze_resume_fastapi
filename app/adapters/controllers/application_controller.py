from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse
from typing import Annotated

from app.adapters.messages.field_messages import build_field_error
from app.adapters.security.internal_auth import verify_internal_token
from app.application.dto.request.update_score_request import UpdateScoreRequest
from app.application.use_cases.application.update_score_use_case import UpdateScoreUseCase
from app.domain.exception.base import ErrorResponse
from app.infrastructure.database.database import depends_db
from app.infrastructure.database.gateway.application_gateway_implementation import ApplicationGatewayImplementation

router = APIRouter(
    prefix="/application",
    tags=["Application"],
)


def update_score_use_case_gateway(db: depends_db):
    application_gateway = ApplicationGatewayImplementation(db)
    return UpdateScoreUseCase(application_gateway)



@router.patch("/{application_id}/score",status_code=status.HTTP_204_NO_CONTENT)
async def update_application_score(
       application_id: UUID,
       body: UpdateScoreRequest,
       update_score_use_case: Annotated[UpdateScoreUseCase,Depends(update_score_use_case_gateway)],
       _: Annotated[None,Depends(verify_internal_token)]
):
    try:
      update_score_use_case(
          score=body.score,
          public_id=str(application_id),
      )
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