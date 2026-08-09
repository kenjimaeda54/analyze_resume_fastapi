from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.adapters.messages.field_messages import build_field_error
from app.domain.exception.base import ErrorResponse
from app.main import app


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields = [build_field_error(err) for err in exc.errors()]
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