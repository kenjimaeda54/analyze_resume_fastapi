from app.application.ports.application_gateway import ApplicationGatewayInterface
from app.domain.exception.application.application_not_found import ApplicationNotFound
from app.domain.rules.status_from_score import status_from_score


class UpdateScoreUseCase:
    def __init__(self,
                 application_gateway_score: ApplicationGatewayInterface
                 ):
        self.application_gateway = application_gateway_score


    def execute(
              self,
              score: float,
              public_id: str
    ) -> None:
      application = self.application_gateway.get_application_by_public_id(public_id)

      if application is None:
          raise ApplicationNotFound(public_id=public_id)


      self.application_gateway.update_score_application(
          score=score,
          status=status_from_score(score),
          public_id=public_id
      )

    def __call__(self, score: float, public_id: str):
        self.execute(
            score=score,
            public_id=public_id
        )






