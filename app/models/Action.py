from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: 
  from app.models import ActionType, Ppda, DeadLine, Kpi, Report, User
  
class ActionBase(SQLModel):
    """Base model class for Action containing common attributes.
    
    Attributes:
        id_ppda (Optional[str]): Foreign key referencing the PPDA this action belongs to
        id_user (Optional[str]): Foreign key referencing the user who created this action
        id_action_type (Optional[int]): Foreign key referencing the type of action
    """
    id_ppda : Optional[str] = Field(default=None, foreign_key="ppda.id_ppda")
    id_user : Optional[str] = Field(default=None, foreign_key="user.id_user")
    id_action_type: Optional[int] = Field(default=None, foreign_key="action_type.id_action_type")
  
class Action(ActionBase, table=True):
    """Database model for actions within the PPDA system.
    
    Inherits from ActionBase and implements the database table structure.
    
    Attributes:
        id_action (Optional[str]): Unique identifier for the action, auto-generated UUID
        action_type (Optional[ActionType]): Relationship to the type of action
        ppda (Optional[Ppda]): Relationship to the parent PPDA
        deadlines (list[DeadLine]): List of deadlines associated with this action
        kpi_list (list[Kpi]): List of KPIs associated with this action
        report (Optional[Report]): Associated report for this action
        user (Optional[User]): Relationship to the user who created this action
    """
    __tablename__ = "action"
    id_action: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
 
    action_type : Optional["ActionType"] = Relationship(back_populates="action") 
    ppda : Optional["Ppda"] = Relationship(back_populates="actions")
    deadlines : list["DeadLine"] = Relationship(back_populates="action")
    kpi_list : list["Kpi"] = Relationship(back_populates="action")
    report : Optional["Report"] = Relationship(back_populates="report_action")
    user: Optional["User"] = Relationship(back_populates="actions")

class ActionCreate(ActionBase):
    """Model for creating new actions.
    
    Inherits from ActionBase and is used for creating new action instances.
    
    Attributes:
        id_ppda (Optional[str]): Foreign key referencing the PPDA this action belongs to
        id_action_type (Optional[int]): Foreign key referencing the type of action
    """
    id_ppda : Optional[str]
    id_action_type: Optional[int]

class ActionUpdate(SQLModel):
    """Model for updating existing actions.
    
    Inherits from SQLModel and is used for updating existing action instances.
    
    Attributes:
        id_ppda (Optional[str]): Foreign key referencing the PPDA this action belongs to
        id_action_type (Optional[int]): Foreign key referencing the type of action
    """
    id_ppda : Optional[str]
    id_action_type: Optional[int]
    id_user : Optional[str]

class ActionPublic(SQLModel):
    """Model for public representation of actions.
    
    Attributes:
        id_ppda (Optional[str]): Foreign key referencing the PPDA this action belongs to
        action_type (Optional[str]): Type of action being performed
    """
    id_ppda : Optional[str]
    action_type : Optional[str]