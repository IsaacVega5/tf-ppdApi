from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action

class ActionTypeBase(SQLModel):
  action_type: Optional[str]
  
class ActionType(ActionTypeBase, table=True):
  __tablename__ = "action_type"
  id_action_type: Optional[int] = Field(default=None, primary_key=True)
  
  action: list["Action"] = Relationship(back_populates="action_type")