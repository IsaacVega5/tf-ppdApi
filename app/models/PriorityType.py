from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Message

class PriorityTypeBase(SQLModel):
  value : Optional[str] = Field(nullable=False)

class PriorityType(PriorityTypeBase, table=True):
  __tablename__ = "priority_type"
  id_priority_type: Optional[int] = Field(default=None, primary_key=True)
  
  messages : list["Message"] = Relationship(back_populates="priority_type")
  
  
