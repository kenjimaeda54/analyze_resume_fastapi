from app.application.ports.application_gateway import ApplicationGatewayInterface
from app.application.ports.candidate_gateway import CandidateGatewayInterface
from app.application.ports.vacancy_gateway import VacancyGatewayInterface
from app.domain.entities.application import Application
from app.domain.entities.candidate import Candidate
from app.domain.exception.vacancy.vancacy_not_found import VacancyNotFound


class ApplyToVacancyUseCase:
    def __init__(self, candidate_gateway: CandidateGatewayInterface,
                 application_gateway: ApplicationGatewayInterface,
                 vacancy_gateway: VacancyGatewayInterface
                 ):
        self.candidate_gateway = candidate_gateway
        self.application_gateway = application_gateway
        self.vacancy_gateway = vacancy_gateway


    def execute(self, candidate: Candidate, public_id: str) -> Application:
         candidate_intern = self.candidate_gateway.get_candidate(cpf=candidate.cpf,email=candidate.email)
         vacancy = self.vacancy_gateway.get_by_vacancy_public_id(public_id)

         if vacancy is None:
             raise VacancyNotFound(public_id)

         assert vacancy.id is not None, "Vacancy should have an ID after fetch"

         if candidate_intern is None:
              candidate_request = candidate.model_copy(update={"public_id": public_id})
              candidate_intern =   self.candidate_gateway.create_candidate(candidate = candidate_request)


         assert  candidate_intern.id is not None, "Candidate should have an ID after get/create"

         application = Application(
              candidate_id=candidate_intern.id,
              vacancy_id=vacancy.id,
         )

         application_intern = self.application_gateway.create_application(application= application)
         return application_intern

    def __call__(self, candidate: Candidate,vacancy_id: str) -> Application:
        return self.execute(candidate, vacancy_id)


