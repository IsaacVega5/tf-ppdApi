from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: 
  from app.models.Institution import Institution

class InstitutionTypeBase(SQLModel):
  """
  Base model containing common fields for Institution Type.
  
  Attributes:
      institution_type (Optional[str]): The classification name for institutions.
          Must be non-null when saved to database (nullable=False).
  """
  institution_type : Optional[str] = Field(nullable=False)

class InstitutionType(InstitutionTypeBase, table=True):
  """
  Database table model for institution types with relationships.
  
  Attributes:
      id_institution_type (int): Primary key identifier
      institution (List[Institution]): Related institutions using this type
      
  Relationships:
      - institutions: One-to-many relationship with Institution model
  """
  __tablename__ = "institution_type"
  id_institution_type : Optional[int] = Field(default=None, primary_key=True)
  
  institution : list["Institution"] = Relationship(back_populates="institution_type")
  
class InstitutionTypeCreate(InstitutionTypeBase):
  """
  Schema for creating new institution types.
  
  Attributes:
      institution_type (str): Required name for the new institution type.
          Must be a non-empty string.
  """
  institution_type : str

class InstitutionTypeUpdate(SQLModel):
  """
  Schema for updating existing institution types.
  
  Attributes:
      institution_type (Optional[str]): New name for the institution type.
  """
  institution_type : Optional[str]