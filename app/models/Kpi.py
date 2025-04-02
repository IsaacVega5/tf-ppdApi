from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import Action, Variable

class KpiBase(SQLModel):
  id_action: Optional[str] = Field(default=None, foreign_key="action.id_action")
  description : Optional[str] = Field(default=None)

class Kpi(KpiBase, table=True):
  __tablename__ = "kpi"
  id_kpi: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  action : Optional["Action"] = Relationship(back_populates="kpi_list")
  variables : list["Variable"] = Relationship(back_populates="kpi")