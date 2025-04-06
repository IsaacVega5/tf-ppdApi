from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import Action, Variable

class KpiBase(SQLModel):
    """Base model class for KPI (Key Performance Indicator) containing common attributes.
    
    Attributes:
        id_action (Optional[str]): Foreign key referencing the action this KPI belongs to
        description (Optional[str]): Detailed description of what this KPI measures
    """
    id_action: Optional[str] = Field(default=None, foreign_key="action.id_action")
    description : Optional[str] = Field(default=None)

class Kpi(KpiBase, table=True):
    """Database model for Key Performance Indicators (KPIs).
    
    Inherits from KpiBase and implements the database table structure.
    
    Attributes:
        id_kpi (Optional[str]): Unique identifier for the KPI, auto-generated UUID
        action (Optional[Action]): Relationship to the associated action
        variables (list[Variable]): List of variables used to calculate this KPI
    """
    __tablename__ = "kpi"
    id_kpi: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    action : Optional["Action"] = Relationship(back_populates="kpi_list")
    variables : list["Variable"] = Relationship(back_populates="kpi")