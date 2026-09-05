from fastapi import FastAPI, status
import uvicorn

from app.adapters.controllers import candidate_controller
from app.adapters.handlers.application.application_exception_handler import application_already_exists_exception
from app.adapters.handlers.resume.resume_exception_handler import resume_exception_extension_handler
from app.adapters.handlers.vacancy.vacancy_exception_handler import vacancy_not_found_exception
from app.domain.exception.application.application_already_exists_exception import ApplicationAlreadyExistsException
from app.domain.exception.candidate.candidate__already_exists_exceptions import CandidateAlreadyExistsException
from app.adapters.handlers.candidate.candidate_exception_handler import candidate_already_exists_exception, \
    candidate_not_found_exception, candidate_conflict
from app.domain.exception.candidate.candidate_conflict import CandidateConflictException
from app.domain.exception.candidate.candidate_not_found import CandidateNotFound
from app.domain.exception.resume.resume_exception_extension_handler import ResumeInvalidExtensionException
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound

app = FastAPI()


@app.get("/healthy", status_code=status.HTTP_200_OK)
async def healthy():
    return {"status": "200"}

app.add_exception_handler(CandidateConflictException,candidate_conflict)
app.add_exception_handler(CandidateAlreadyExistsException, candidate_already_exists_exception)
app.add_exception_handler(CandidateNotFound, candidate_not_found_exception)
app.add_exception_handler(ResumeInvalidExtensionException, resume_exception_extension_handler)
app.add_exception_handler(VacancyNotFound, vacancy_not_found_exception)
app.add_exception_handler(ApplicationAlreadyExistsException,application_already_exists_exception)
app.include_router(candidate_controller.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)