from starlette import status
from fastapi import FastAPI
import uvicorn

from app.adapters.controllers import candidate_controller
from app.domain.exception.candidate_exception import CandidateAlreadyExistsException
from app.infrastructure.exceptions.candidate_already_exception import candidate_already_exists_exception

app = FastAPI()


@app.get("/healthy",status_code=status.HTTP_200_OK)
async def healthy():
    return {"status": "200"}

app.add_exception_handler(CandidateAlreadyExistsException,candidate_already_exists_exception)
app.include_router(candidate_controller.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)