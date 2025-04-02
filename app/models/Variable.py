from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: 
  from app.models import Kpi, History

class VariableBase(SQLModel):
  id_kpi : Optional[str] = Field(default=None, foreign_key="kpi.id_kpi")
  formula: Optional[str] = Field(default=None)
  verification_medium : Optional[str] = Field(default=None)

class Variable(VariableBase, table=True):
  __tablename__ = "variable"
  id_variable: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  kpi : Optional["Kpi"] = Relationship(back_populates="variables")
  history_list : list["History"] = Relationship(back_populates="variable")