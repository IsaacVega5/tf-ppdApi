from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import UserInstitution

class UserRolBase(SQLModel):
  """
  Base model for User Role definitions.
  
  Represents different role types that users can have within institutions
  
  Attributes:
      user_rol_name (str): Name of the role (required, non-nullable).
          Examples: 'Administrator', 'Researcher', 'Reviewer'
  """
  user_rol_name : Optional[str] = Field(nullable=False)
  
class UserRol(UserRolBase, table=True):
  """
  Database model for User Roles.
  
  Represents distinct permission sets/access levels that users can be assigned
  when associated with institutions through the UserInstitution junction table.
  
  Attributes:
      id_user_rol (int): Auto-incrementing primary key
      user_institution_user_rol (List[UserInstitution]): Collection of user-institution
          associations that use this role
  
  Relationships:
      - user_institution_user_rol: One-to-many relationship with UserInstitution
  """
  __tablename__ = "user_rol"
  
  id_user_rol : Optional[int] = Field(default=None, primary_key=True)
  
  user_institution_user_rol : list["UserInstitution"] = Relationship(back_populates="user_rol")