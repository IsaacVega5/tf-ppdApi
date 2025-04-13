from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import User, Institution, UserRol

class UserInstitutionBase(SQLModel):
  """
  Base model for User-Institution association (junction table).
  
  Represents the many-to-many relationship between Users and Institutions,
  with additional role information through UserRol.
  
  Attributes:
      id_user (str): Composite primary key - references User.id_user
      id_institution (str): Composite primary key - references Institution.id_institution
      id_user_rol (Optional[int]): Foreign key to UserRol, defines user's role in institution
      is_active (bool): Flag indicating if the association is active
  """
  id_user : Optional[str] = Field(default=None, foreign_key="user.id_user", primary_key=True)
  id_institution : Optional[str] = Field(default=None, foreign_key="institution.id_institution", primary_key=True)
  id_user_rol : Optional[int] = Field(default=None, foreign_key="user_rol.id_user_rol")
  is_active : bool = Field(default=True, nullable=False)
  
class UserInstitution(UserInstitutionBase, table=True):
  """
  Database model for User-Institution association table.
  
  This junction table implements a many-to-many relationship between
  Users and Institutions with additional attributes (role assignment).
  
  Attributes:
      user (User): Associated User entity
      institution_user_institution (Institution): Associated Institution entity
      user_rol (Optional[UserRol]): Role assignment for this association
  
  Relationships:
      - user: Links back to User.user_institution_user
      - institution_user_institution: Links back to Institution.user_institution_institution
      - user_rol: Links back to UserRol.user_institution_user_rol
  """
  __tablename__ = "user_institution"
  
  user : "User" = Relationship(back_populates="user_institution_user")
  institution_user_institution : "Institution" = Relationship(back_populates="user_institution_institution")
  user_rol : Optional["UserRol"] = Relationship(back_populates="user_institution_user_rol")

class UserInstitutionPublic(UserInstitutionBase):
  """
  Public representation of UserInstitution for serialization purposes.
  
  Attributes:
      id_user (str): Composite primary key - references User.id_user
      id_institution (str): Composite primary key - references Institution.id_institution
  """
  id_user : Optional[str]
  id_institution : Optional[str]
  is_active : Optional[bool]
  user_rol : Optional[str]

class UserInstitutionCreate(UserInstitutionBase):
  """
  Model for creating a new UserInstitution association in the database.
  
  Attributes:
      id_user (str): Composite primary key - references User.id_user
      id_institution (str): Composite primary key - references Institution.id_institution
      id_user_rol (Optional[int]): Foreign key to UserRol, defines user's role in institution
      is_active (bool): Flag indicating if the association is active
  """
  id_user : Optional[str]
  id_institution : Optional[str]
  id_user_rol : Optional[int]

class UserInstitutionUpdate(UserInstitutionBase):
  """
  Model for updating an existing UserInstitution association in the database.
  
  Attributes:
      id_user (str): Composite primary key - references User.id_user
      id_institution (str): Composite primary key - references Institution.id_institution
      id_user_rol (Optional[int]): Foreign key to UserRol, defines user's role in institution
      is_active (bool): Flag indicating if the association is active
  """
  id_user : Optional[str]
  id_institution : Optional[str]
  id_user_rol : Optional[int] = None
  is_active : Optional[bool] = None