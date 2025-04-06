from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Message

class PriorityTypeBase(SQLModel):
    """Base model class for PriorityType containing common attributes.
    
    Attributes:
        value (Optional[str]): The priority level description (required field)
    """
    value : Optional[str] = Field(nullable=False)

class PriorityType(PriorityTypeBase, table=True):
    """Database model for message priority types.
    
    Inherits from PriorityTypeBase and implements the database table structure.
    
    Attributes:
        id_priority_type (Optional[int]): Primary key identifier for the priority type
        messages (list[Message]): List of messages with this priority level
    """
    __tablename__ = "priority_type"
    id_priority_type: Optional[int] = Field(default=None, primary_key=True)
    
    messages : list["Message"] = Relationship(back_populates="priority_type")
  
  
