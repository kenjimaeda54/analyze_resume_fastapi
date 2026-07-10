
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Float

from app.domain.enum.candidate_status import CandidateStatus
from app.infrastructure.database.database import Base


class CandidateTable(Base):
     __tablename__ = 'candidate'


     id = Column(Integer, primary_key=True,index=True)
     cpf = Column(String(15),unique=True, nullable=False)
     resume_path = Column(String(15),nullable=False)
     vacancy_id = Column(Integer,nullable=True)
     score = Column(Float,nullable=False)
     status = Column(SAEnum(CandidateStatus), default=CandidateStatus.PENDING)




