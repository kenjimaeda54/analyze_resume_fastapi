from typing import cast
from starlette.requests import Request

from starlette import status

from app.domain.exception.candidate.candidate_exceptions import CandidateAlreadyExistsException
from app.domain.exception.base import ErrorResponse
from fastapi.responses import JSONResponse

from app.domain.exception.candidate.candidate_not_found import CandidateNotFound


async def candidate_already_exists_exception(request: Request, exception: Exception):
    candidate_exception = cast(CandidateAlreadyExistsException, exception)
    error_response = ErrorResponse(
        http_status_code=status.HTTP_409_CONFLICT,
        error_code=candidate_exception.error_code,
        message=str(exception)
    )
    return JSONResponse(
        status_code=error_response.http_status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def candidate_not_found_exception(request: Request, exception: Exception) -> JSONResponse:
    candidate_exception = cast(CandidateNotFound, exception)
    error_response = ErrorResponse(
        http_status_code=status.HTTP_404_NOT_FOUND,
        error_code=candidate_exception.error_code,
        message=str(exception)
    )
    return JSONResponse(
        status_code=error_response.http_status_code,
        content=error_response.model_dump(exclude_none=True),
    )