from app.application.ports.application_gateway import ApplicationGatewayInterface
from app.application.ports.candidate_gateway import CandidateGatewayInterface
from app.application.ports.storage_r2_gateway import StorageR2GatewayInterface
from app.application.ports.vacancy_gateway import VacancyGatewayInterface
from app.domain.exception.application.application_already_exists_exception import ApplicationAlreadyExistsException
from app.domain.exception.candidate.candidate_conflict import CandidateConflictException
from app.domain.exception.candidate.candidate_cpf_exception import CandidateCpfException
from app.domain.exception.candidate.candidate_exception import CandidateException
from app.infrastructure.storage.validators.candidate.validate_cpf import validate_cpf
from app.infrastructure.storage.validators.candidate.validate_resume_extension import validate_resume_extension
from app.domain.entities.application import Application
from app.domain.entities.candidate import Candidate
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound


class ApplyToVacancyUseCase:
    def __init__(self, candidate_gateway: CandidateGatewayInterface,
                 application_gateway: ApplicationGatewayInterface,
                 vacancy_gateway: VacancyGatewayInterface,
                 storager2: StorageR2GatewayInterface,
                 ):
        self.candidate_gateway = candidate_gateway
        self.application_gateway = application_gateway
        self.vacancy_gateway = vacancy_gateway
        self.storager2 = storager2

    def execute(
            self,
            candidate: Candidate,
            vacancy_public_id: str,
            resume_bytes: bytes,
            resume_content_type: str | None,
    ) -> Application:
        extension = validate_resume_extension(resume_bytes=resume_bytes, content_type=resume_content_type)

        if not validate_cpf(candidate.cpf):
            raise CandidateCpfException()

        candidate_intern = self.candidate_gateway.get_candidate(cpf=candidate.cpf, email=candidate.email)
        vacancy = self.vacancy_gateway.get_by_vacancy_public_id(vacancy_public_id)

        if vacancy is None:
            raise VacancyNotFound(vacancy_public_id)

        assert vacancy.id is not None, "Vacancy should have an ID after fetch"

        if candidate_intern is not None and (
                candidate_intern.cpf != candidate.cpf or candidate_intern.email != candidate.email
        ):
            raise CandidateConflictException()

        if candidate_intern is not None:
            assert candidate_intern.id is not None, "Candidate should have an ID"
            existing_application = self.application_gateway.find_by_candidate_and_vacancy(
                candidate_id=candidate_intern.id,
                vacancy_id=vacancy.id,
            )
            if existing_application is not None:
                raise ApplicationAlreadyExistsException()

        file_path = f"resumes/{candidate.cpf}_{vacancy_public_id}.{extension}"
        resume_url = self.storager2.upload_file(file_content=resume_bytes, file_path=file_path)

        try:
            if candidate_intern is None:
                candidate_request = candidate.model_copy(update={"resume_url": resume_url})
                candidate_intern = self.candidate_gateway.create_candidate(candidate=candidate_request)
            else:
                candidate_intern = self.candidate_gateway.update_resume_url(
                    candidate_cpf=candidate_intern.cpf,
                    resume_url=resume_url,
                )

            assert candidate_intern.id is not None, "Candidate should have an ID after get/create"

            application = Application(
                candidate_id=candidate_intern.id,
                vacancy_id=vacancy.id,
                resume_url=resume_url,
            )

            return self.application_gateway.create_application(application=application)

        except Exception:
            self.storager2.delete_file(file_path=file_path)
            raise

    def __call__(self, candidate: Candidate,vacancy_id: str,resume_bytes: bytes,resume_content: str | None) -> Application:
        return self.execute(candidate=candidate,
                            vacancy_public_id= vacancy_id,
                            resume_bytes=resume_bytes,
                            resume_content_type= resume_content)


