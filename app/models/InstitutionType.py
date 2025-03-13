from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: 
  from app.models.Institution import Institution

class InstitutionTypeBase(SQLModel):
  institution_type : Optional[str] = Field(nullable=False)

class InstitutionType(InstitutionTypeBase, table=True):
  __tablename__ = "institution_type"
  id_institution_type : Optional[int] = Field(default=None, primary_key=True)
  
  institution : list["Institution"] = Relationship(back_populates="institution_type")
  
class InstitutionTypeCreate(InstitutionTypeBase):
  institution_type : str

class InstitutionTypeUpdate(SQLModel):
  institution_type : Optional[str]