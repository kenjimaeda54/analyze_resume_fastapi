from sqlalchemy import select, Sequence
from sqlalchemy.orm import Session

from app.adapters.mapper.application_mapper import ApplicationMapper
from app.application.ports.application_gateway import ApplicationGatewayInterface
from app.domain.entities.application import Application
from app.infrastructure.database.models.application_table import ApplicationTable
from app.infrastructure.database.models.vacancy_table import VacancyTable


class ApplicationGatewayImplementation(ApplicationGatewayInterface):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    #não posso recuperar os candidatos que estão com as vagas deletadas
    def get_application(self, vacancy_id: int,candidate_id: int) -> Sequence[Application]:
        #O JOIN existe porque o campo que eu quero filtrar (deleted_at) só existe na tabela VacancyTable.
        # Então eu 'colo' temporariamente as informações de VacancyTable e ApplicationTable
        # (relacionando pela chave em comum vacancy_id = id),
        # e a partir dessa combinação temporária, consigo filtrar usando colunas de qualquer uma
        # das duas tabelas.
        statement = (select(ApplicationTable)
                     .join(VacancyTable, ApplicationTable.vacancy_id == vacancy_id)
                     .where(ApplicationTable.candidate_id == candidate_id,
                                                   VacancyTable.delete_at.is_(None)))
        application_db: Sequence[ApplicationTable] = self.db_session.execute(statement).scalars().all()

        if application_db is None:
            return None

        return ApplicationMapper.to_domain_from_table(application_db)

    def create_application(self, application: Application) -> Application:
        #lembrando que para relações e index utilizamos o id não publi_id
        #ou seja para exterior sempre public_id , interno e o id
        try:
            application_table = ApplicationTable(
                candidate_id=application.candidate_id,
                vacancy_id=application.vacancy_id,
                score=application.score,
                status=application.status,
            )
            self.db_session.add(application_table)
            self.db_session.commit()
            self.db_session.refresh(application_table)

            return ApplicationMapper.to_table_from_domain(application_table)

        except Exception as e:
            self.db_session.rollback()
            raise e