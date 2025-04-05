from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import Action, History

class ReportBase(SQLModel):
  id_action : Optional[str] = Field(nullable=False, foreign_key="action.id_action")

class Report(ReportBase, table=True):
  __tablename__ = "report"
  
  id_report : Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  report_action : Optional["Action"] = Relationship(back_populates="report")
  history_list : list["History"] = Relationship(back_populates="report")
