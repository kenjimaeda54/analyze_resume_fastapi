from typing import cast
from urllib.request import Request

from starlette import status
from starlette.responses import JSONResponse

from app.domain.exception.base import ErrorResponse
from app.domain.exception.resume.resume_exception_extension_handler import ResumeInvalidExtensionException


async def resume_exception_extension_handler(request: Request, exception: Exception) -> JSONResponse:
     resume_exception = cast(ResumeInvalidExtensionException, exception)
     error_response = ErrorResponse(
         http_status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
         error_code=resume_exception.error_code,
         message=str(resume_exception)
     )
     return JSONResponse(
         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
         content=error_response.model_dump(exclude_none=True),
     )