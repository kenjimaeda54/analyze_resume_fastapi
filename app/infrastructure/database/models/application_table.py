import uuid

from sqlalchemy import Integer, ForeignKey, Float, Uuid, text, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SAEnum


from app.domain.enum.candidate_status import CandidateStatus
from app.infrastructure.database.database import Base


class ApplicationTable(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,index=True,autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        server_default=text("gen_random_uuid()"),
        unique=True,
        nullable=False
    )
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate.id"),nullable=False)
    resume_url: Mapped[str] = mapped_column(String(255), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancy.id"),nullable=False)
    score: Mapped[float | None] = mapped_column(Float,nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(SAEnum(CandidateStatus),nullable=False,default=CandidateStatus.PENDING)

    #garantir que o candidato não vai aderir a mesma vaga duas vezes
    #candidate_id + vacancy_id se for iguais da erro
    #name e apenas um rotulo
    __table_args__ = (
        UniqueConstraint("candidate_id", "vacancy_id", name="uq_candidate_vacancy"),
    )