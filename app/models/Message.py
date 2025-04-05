import uuid
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import PriorityType, DeadLine

class MessageBase(SQLModel):
  id_deadline : Optional[str] = Field(default=None, foreign_key="deadline.id_deadline")
  id_priority_type : Optional[int] = Field(default=None, foreign_key="priority_type.id_priority_type")
  value: Optional[str] = Field(default=None)
  time_before : Optional[int] = Field(default=None)
  
class Message(MessageBase, table=True):
  __tablename__ = "message"
  id_message: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  priority_type : Optional["PriorityType"] = Relationship(back_populates="messages")
  deadline : Optional["DeadLine"] = Relationship(back_populates="deadline_messages")