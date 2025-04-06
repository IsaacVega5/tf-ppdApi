from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: 
  from app.models import Kpi, History

class VariableBase(SQLModel):
    """Base model class for Variable containing common attributes.
    
    Attributes:
        id_kpi (Optional[str]): Foreign key referencing the KPI this variable belongs to
        formula (Optional[str]): Mathematical or logical formula used to calculate the variable
        verification_medium (Optional[str]): Method or source used to verify the variable's value
    """
    id_kpi : Optional[str] = Field(default=None, foreign_key="kpi.id_kpi")
    formula: Optional[str] = Field(default=None)
    verification_medium : Optional[str] = Field(default=None)

class Variable(VariableBase, table=True):
    """Database model for variables associated with KPIs.
    
    Inherits from VariableBase and implements the database table structure.
    
    Attributes:
        id_variable (Optional[str]): Unique identifier for the variable, auto-generated UUID
        kpi (Optional[Kpi]): Relationship to the associated KPI
        history_list (list[History]): List of historical records for this variable
    """
    __tablename__ = "variable"
    id_variable: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    kpi : Optional["Kpi"] = Relationship(back_populates="variables")
    history_list : list["History"] = Relationship(back_populates="variable")