from fastapi import FastAPI, status
import uvicorn
from fastapi.exceptions import RequestValidationError

from app.adapters.controllers import candidate_controller
from app.adapters.handlers.core import request_validation_error
from app.adapters.handlers.vacancy.vacancy_exception_handler import vacancy_not_found_exception
from app.domain.exception.candidate.candidate_exceptions import CandidateAlreadyExistsException
from app.adapters.handlers.candidate.candidate_exception_handler import candidate_already_exists_exception, \
    candidate_not_found_exception
from app.domain.exception.candidate.candidate_not_found import CandidateNotFound
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound

app = FastAPI()


@app.get("/healthy", status_code=status.HTTP_200_OK)
async def healthy():
    return {"status": "200"}

app.add_exception_handler(CandidateAlreadyExistsException, candidate_already_exists_exception)
app.add_exception_handler(CandidateNotFound, candidate_not_found_exception)
app.add_exception_handler(VacancyNotFound, vacancy_not_found_exception)
app.include_router(candidate_controller.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)