from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: 
  from app.models import ActionType, Ppda
  
class ActionBase(SQLModel):
  id_ppda : Optional[str] = Field(default=None, foreign_key="ppda.id_ppda")
  rut_creator: Optional[str] = Field(default=None)
  id_action_type: Optional[int] = Field(default=None, foreign_key="action_type.id_action_type")
  
class Action(ActionBase, table=True):
  __tablename__ = "action"
  id_action: Optional[int] = Field(default=None, primary_key=True)
 
  action_type : Optional["ActionType"] = Relationship(back_populates="action") 
  ppda : Optional["Ppda"] = Relationship(back_populates="actions")