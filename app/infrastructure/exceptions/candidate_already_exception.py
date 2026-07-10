from typing import cast
from urllib.request import Request

from starlette import status

from app.domain.exception.candidate_exception import CandidateAlreadyExistsException
from app.domain.exception.common import ErrorResponse
from fastapi.responses import JSONResponse

async def candidate_already_exists_exception(request: Request,exception: Exception):
    candidate_exception = cast(CandidateAlreadyExistsException,exception)
    error_response = ErrorResponse(http_status_code=status.HTTP_409_CONFLICT,error_code=candidate_exception.error_code,message=str(exception))
    return JSONResponse(
        status_code=error_response.http_status_code,
        content=error_response.model_dump(exclude_none=True),
    )
