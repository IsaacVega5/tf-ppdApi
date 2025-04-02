import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import Report, Variable

class HistoryBase(SQLModel):
  id_report : Optional[str] = Field(default=None, foreign_key="report.id_report")
  id_variable : Optional[str] = Field(default=None, foreign_key="variable.id_variable")
  value : Optional[str] = Field(default=None)
  created_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
  updated_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()), sa_column_kwargs={"onupdate": int(datetime.datetime.now(datetime.timezone.utc).timestamp())})

class History(HistoryBase, table=True):
  __tablename__ = "history"
  id_history : Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  report : Optional["Report"] = Relationship(back_populates="history_list")
  variable : Optional["Variable"] = Relationship(back_populates="history_list")