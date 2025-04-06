
from typing import TYPE_CHECKING, Optional
from pydantic import field_validator
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from app.models import InstitutionType, UserInstitution, Ppda

class InstitutionBase(SQLModel):
  """
  Base model for Institution containing common fields.
  
  Attributes:
      institution_name (Optional[str]): Name of the institution.
      id_institution_type (Optional[int]): Foreign key to institution type.
  """
  institution_name: Optional[str] = Field(nullable=True)
  id_institution_type: Optional[int] = Field(default=None, foreign_key="institution_type.id_institution_type")

class Institution(InstitutionBase, table=True):
  """
  Database model for Institution with relationships.
  
  Attributes:
      id_institution (str): Primary key (UUID format).
      institution_type (Optional[InstitutionType]): Related institution type.
      user_institution_institution (List[UserInstitution]): Related user institutions.
  """
  __tablename__ = "institution"
  
  id_institution: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  
  institution_type : Optional["InstitutionType"] = Relationship(back_populates="institution")
  user_institution_institution : list["UserInstitution"] = Relationship(back_populates="institution_user_institution")
  ppda_list : list["Ppda"] = Relationship(back_populates="institution")
  
class InstitutionCreate(InstitutionBase):
  """
  Model for creating new institutions with validation.
  
  Attributes:
      institution_name (str): Required name of the institution.
      id_institution_type (int): Required institution type reference.
  
  Validations:
      - Institution name cannot be empty or just whitespace.
  """
  institution_name: str
  id_institution_type: int

  @field_validator('institution_name')
  def name_must_not_be_empty(cls, v):
    """
    Validate that institution name is not empty.
    
    Args:
        v (str): Input name to validate
        
    Returns:
        str: Stripped name if valid
        
    Raises:
        ValueError: If name is empty or whitespace only
    """
    if not v or not v.strip():
      raise ValueError("The institution name must not be empty")
    return v.strip()

class InstitutionUpdate(InstitutionBase):
  """
  Model for updating institutions with optional fields.
  
  Attributes:
      institution_name (Optional[str]): New name (optional update).
      id_institution_type (Optional[int]): New type reference (optional update).
  """
  institution_name: Optional[str] = None
  id_institution_type: Optional[int] = None