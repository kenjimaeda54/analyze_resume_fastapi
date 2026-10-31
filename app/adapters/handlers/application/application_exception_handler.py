from typing import cast

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.exception.application.application_already_exists_exception import ApplicationAlreadyExistsException
from app.domain.exception.application.application_not_found import ApplicationNotFound
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


async  def application_not_found_exception(request: Request, exception: Exception) -> JSONResponse:
    application_not_found = cast(ApplicationNotFound,exception)
    error_response = ErrorResponse(
        http_status_code=status.HTTP_404_NOT_FOUND,
        error_code=application_not_found.error_code,
        message=str(application_not_found)
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response.model_dump(exclude_none=True)
    )


