from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: 
  from app.models import ActionType, Ppda, DeadLine, Kpi, Report
  
class ActionBase(SQLModel):
  id_ppda : Optional[str] = Field(default=None, foreign_key="ppda.id_ppda")
  rut_creator: Optional[str] = Field(default=None)
  id_action_type: Optional[int] = Field(default=None, foreign_key="action_type.id_action_type")
  
class Action(ActionBase, table=True):
  __tablename__ = "action"
  id_action: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
 
  action_type : Optional["ActionType"] = Relationship(back_populates="action") 
  ppda : Optional["Ppda"] = Relationship(back_populates="actions")
  deadlines : list["DeadLine"] = Relationship(back_populates="action")
  kpi_list : list["Kpi"] = Relationship(back_populates="action")
  report : Optional["Report"] = Relationship(back_populates="report_action")