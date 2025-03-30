
from typing import TYPE_CHECKING, Optional
from pydantic import field_validator
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import InstitutionType, UserInstitution, Ppda

class InstitutionBase(SQLModel):
  institution_name: Optional[str] = Field(nullable=True)
  id_institution_type: Optional[int] = Field(default=None, foreign_key="institution_type.id_institution_type")

class Institution(InstitutionBase, table=True):
  __tablename__ = "institution"
  
  id_institution: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  
  institution_type : Optional["InstitutionType"] = Relationship(back_populates="institution")
  user_institution_institution : list["UserInstitution"] = Relationship(back_populates="institution_user_institution")
  ppda : Optional["Ppda"] = Relationship(back_populates="institutions")
  
class InstitutionCreate(InstitutionBase):
  institution_name: str
  id_institution_type: int

  @field_validator('institution_name')
  def name_must_not_be_empty(cls, v):
    if not v or not v.strip():
      raise ValueError("The institution name must not be empty")
    return v.strip()

class InstitutionUpdate(InstitutionBase):
  institution_name: Optional[str] = None
  id_institution_type: Optional[int] = None