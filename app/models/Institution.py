
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import InstitutionType, UserInstitution

class InstitutionBase(SQLModel):
  institution_name: Optional[str] = Field(nullable=False)
  id_institution_type: Optional[int] = Field(default=None, foreign_key="institution_type.id_institution_type")

class Institution(InstitutionBase, table=True):
  __tablename__ = "institution"
  
  id_institution: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  
  institution_type : Optional["InstitutionType"] = Relationship(back_populates="institution")
  user_institution_institution : list["UserInstitution"] = Relationship(back_populates="institution_user_institution")