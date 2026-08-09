from typing import cast

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.exception.base import ErrorResponse
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound


async def vacancy_not_found_exception(request: Request, exception: Exception) -> JSONResponse:
    vacancy_not_found =  cast(VacancyNotFound, exception)
    error_response = ErrorResponse(
        http_status_code=status.HTTP_404_NOT_FOUND,
        error_code=vacancy_not_found.error_code,
        message=str(vacancy_not_found),
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                        content=error_response.model_dump(exclude_none=True))