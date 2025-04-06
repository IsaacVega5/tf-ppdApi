from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action

class ActionTypeBase(SQLModel):
    """Base model class for ActionType containing common attributes.
    
    Attributes:
        action_type (Optional[str]): Description of the action type
    """
    action_type: Optional[str]
  
class ActionType(ActionTypeBase, table=True):
    """Database model for types of actions.
    
    Inherits from ActionTypeBase and implements the database table structure.
    
    Attributes:
        id_action_type (Optional[int]): Primary key identifier for the action type
        action (list[Action]): List of actions of this type
    """
    __tablename__ = "action_type"
    id_action_type: Optional[int] = Field(default=None, primary_key=True)
    
    action: list["Action"] = Relationship(back_populates="action_type")