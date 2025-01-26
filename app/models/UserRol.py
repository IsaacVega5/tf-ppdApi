from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import UserInstitution

class UserRolBase(SQLModel):
  user_rol_name : Optional[str] = Field(nullable=False)
  
class UserRol(UserRolBase, table=True):
  __tablename__ = "user_rol"
  
  id_user_rol : Optional[int] = Field(default=None, primary_key=True)
  
  user_institution_user_rol : list["UserInstitution"] = Relationship(back_populates="user_rol")