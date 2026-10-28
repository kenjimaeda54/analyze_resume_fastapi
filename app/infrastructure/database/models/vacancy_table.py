import uuid
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base

class VacancyTable(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True,autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        server_default=text("gen_random_uuid()"),
        unique=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    list_key_words: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, server_default=text("'{}'"))
    delete_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True,default=None)