from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import User, Institution, UserRol

class UserInstitutionBase(SQLModel):
  id_user : Optional[str] = Field(default=None, foreign_key="user.id_user", primary_key=True)
  id_institution : Optional[str] = Field(default=None, foreign_key="institution.id_institution", primary_key=True)
  id_user_rol : Optional[int] = Field(default=None, foreign_key="user_rol.id_user_rol")
  
class UserInstitution(UserInstitutionBase, table=True):
  __tablename__ = "user_institution"
  
  user : "User" = Relationship(back_populates="user_institution_user")
  institution_user_institution : "Institution" = Relationship(back_populates="user_institution_institution")
  user_rol : Optional["UserRol"] = Relationship(back_populates="user_institution_user_rol")