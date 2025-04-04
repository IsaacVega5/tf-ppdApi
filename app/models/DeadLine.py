from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action, Message

class DeadLineBase(SQLModel):
  deadline_date: Optional[datetime] = Field(nullable=False)
  id_action : Optional[str] = Field(default=None, foreign_key="action.id_action")
  year : Optional[int] = Field(default=None)
  
class DeadLine(DeadLineBase, table=True):
  __tablename__ = "deadline"
  id_deadline : Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  action : Optional["Action"] = Relationship(back_populates="deadlines")
  deadline_messages : list["Message"] = Relationship(back_populates="deadline")
