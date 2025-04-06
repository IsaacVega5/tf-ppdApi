from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import Action, History

class ReportBase(SQLModel):
    """Base model class for Report containing common attributes.
    
    Attributes:
        id_action (Optional[str]): Foreign key referencing the action this report belongs to (required field)
    """
    id_action : Optional[str] = Field(nullable=False, foreign_key="action.id_action")

class Report(ReportBase, table=True):
    """Database model for reports associated with actions.
    
    Inherits from ReportBase and implements the database table structure.
    
    Attributes:
        id_report (Optional[str]): Unique identifier for the report, auto-generated UUID
        report_action (Optional[Action]): Relationship to the associated action
        history_list (list[History]): List of historical records for this report
    """
    __tablename__ = "report"
    
    id_report : Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    report_action : Optional["Action"] = Relationship(back_populates="report")
    history_list : list["History"] = Relationship(back_populates="report")
