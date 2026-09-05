import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Float, DateTime, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enum.candidate_status import CandidateStatus
from app.infrastructure.database.database import Base


class CandidateTable(Base):
    __tablename__ = 'candidate'

    id: Mapped[int] = mapped_column(Integer, primary_key=True,index=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        server_default=text("gen_random_uuid()"),
        unique=True,
        nullable=False
    )
    cpf: Mapped[str] = mapped_column(String, index=True,unique=True,nullable=False)
    resume_url: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime,  nullable=True,default=None)



