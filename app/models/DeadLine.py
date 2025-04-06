from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action, Message

class DeadLineBase(SQLModel):
    """Base model class for DeadLine containing common attributes.
    
    Attributes:
        deadline_date (Optional[datetime]): The date and time of the deadline (required)
        id_action (Optional[str]): Foreign key referencing the action this deadline belongs to
        year (Optional[int]): The year associated with this deadline
    """
    deadline_date: Optional[datetime] = Field(nullable=False)
    id_action : Optional[str] = Field(default=None, foreign_key="action.id_action")
    year : Optional[int] = Field(default=None)
  
class DeadLine(DeadLineBase, table=True):
    """Database model for deadlines associated with actions.
    
    Inherits from DeadLineBase and implements the database table structure.
    
    Attributes:
        id_deadline (Optional[str]): Unique identifier for the deadline, auto-generated UUID
        action (Optional[Action]): Relationship to the associated action
        deadline_messages (list[Message]): List of messages related to this deadline
    """
    __tablename__ = "deadline"
    id_deadline : Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    action : Optional["Action"] = Relationship(back_populates="deadlines")
    deadline_messages : list["Message"] = Relationship(back_populates="deadline")
