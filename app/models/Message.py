import uuid
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import PriorityType, DeadLine

class MessageBase(SQLModel):
    """Base model class for Message containing common attributes.
    
    Attributes:
        id_deadline (Optional[str]): Foreign key referencing the deadline this message is associated with
        id_priority_type (Optional[int]): Foreign key referencing the priority level of this message
        value (Optional[str]): The content of the message
        time_before (Optional[int]): Time in advance to send the message before the deadline
    """
    id_deadline : Optional[str] = Field(default=None, foreign_key="deadline.id_deadline")
    id_priority_type : Optional[int] = Field(default=None, foreign_key="priority_type.id_priority_type")
    value: Optional[str] = Field(default=None)
    time_before : Optional[int] = Field(default=None)
  
class Message(MessageBase, table=True):
    """Database model for messages related to deadlines.
    
    Inherits from MessageBase and implements the database table structure.
    
    Attributes:
        id_message (Optional[str]): Unique identifier for the message, auto-generated UUID
        priority_type (Optional[PriorityType]): Relationship to the message's priority level
        deadline (Optional[DeadLine]): Relationship to the associated deadline
    """
    __tablename__ = "message"
    id_message: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    priority_type : Optional["PriorityType"] = Relationship(back_populates="messages")
    deadline : Optional["DeadLine"] = Relationship(back_populates="deadline_messages")