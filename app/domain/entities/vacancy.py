from pydantic import BaseModel


class Vacancy(BaseModel):
      public_id: str | None = None
      id: int | None = None
      title: str
      description: str
      company: str
      list_word_keys: list[str] = []

