import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

load_dotenv()

database_password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")
database_user_name = os.getenv("DB_USER_NAME")

DATABASE_URL = f"postgresql://{database_user_name}:{database_password}@localhost/{database_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


depends_db = Annotated[Session, Depends(get_database)]