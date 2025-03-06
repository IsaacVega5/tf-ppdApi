import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING: from app.models import UserInstitution

class UserBase(SQLModel):
  username: Optional[str] = Field(nullable=True, default=None)
  email: Optional[str] = Field(nullable=False, default=None)
  created_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
  updated_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()), sa_column_kwargs={"onupdate": int(datetime.datetime.now(datetime.timezone.utc).timestamp())})
  
class User(UserBase, table=True):
  __tablename__ = "user"
  
  id_user: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  password : Optional[str] = Field(nullable=False)
  
  user_institution_user : list["UserInstitution"] = Relationship(back_populates="user")
  
class UserCreate(UserBase):
  username: Optional[str]
  email: str
  password : str

class UserLogin(UserBase):
  email: str
  password : str