from typing import cast

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.exception.application.application_already_exists_exception import ApplicationAlreadyExistsException
from app.domain.exception.base import ErrorResponse


async def application_already_exists_exception(request: Request,exception: Exception) -> JSONResponse:
    application_already_exist = cast(ApplicationAlreadyExistsException,exception)
    error_response = ErrorResponse(
       http_status_code=status.HTTP_409_CONFLICT,
       error_code=application_already_exist.error_code,
       message=str(exception)
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump(exclude_none=True)
    )





