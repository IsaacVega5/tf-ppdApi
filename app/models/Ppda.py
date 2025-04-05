from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action, Institution

class PpdaBase(SQLModel):
  id_institution: Optional[str] = Field(default=None, foreign_key="institution.id_institution")

class Ppda(PpdaBase, table=True):
  __tablename__ = "ppda"
  id_ppda: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  
  actions : list["Action"] = Relationship(back_populates="ppda")
  institution : Optional["Institution"] = Relationship(back_populates="ppda_list")
  
class PpdaCreate(PpdaBase):
  id_institution: Optional[str]

class PpdaUpdate(PpdaBase):
  id_institution: Optional[str]