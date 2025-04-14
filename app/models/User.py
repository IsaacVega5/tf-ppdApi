import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr

if TYPE_CHECKING:
  from app.models import UserInstitution, RefreshToken, Action

class UserBase(SQLModel):
  """
  Base model for User containing common fields.
  
  Attributes:
      username (Optional[str]): User's display name.
      email (Optional[str]): User's email address (required in child models).
      created_at (int): Timestamp of user creation.
      updated_at (int): Timestamp of last update.
  """
  username: Optional[str] = Field(nullable=True, default=None)
  email: Optional[str] = Field(nullable=False, default=None)
  created_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
  updated_at : int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()), sa_column_kwargs={"onupdate": int(datetime.datetime.now(datetime.timezone.utc).timestamp())})
  is_admin: bool = Field(default=False)

class User(UserBase, table=True):
  """
  Database model for User with authentication fields.
  
  Attributes:
      id_user (str): Unique UUID identifier (primary key).
      password (str): Hashed password (required).
      user_institution_user (List[UserInstitution]): Relationship to institutions.
      actions (List[Action]): Relationship to actions.
  """
  __tablename__ = "user"
  
  id_user: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
  password : Optional[str] = Field(nullable=False)
  
  user_institution_user : list["UserInstitution"] = Relationship(back_populates="user")
  refresh_token: list["RefreshToken"] = Relationship(back_populates="user")
  actions : list["Action"] = Relationship(back_populates="user")
  
class UserCreate(UserBase):
  """
  Model for user creation with required fields.
  
  Attributes:
      username (Optional[str]): Optional display name.
      email (str): Required email address.
      password (str): Plain text password (will be hashed).
  """
  username: Optional[str]
  email: EmailStr  # Validación automática de email
  password : str

class UserLogin(UserBase):
  """
  Model for user login credentials.
  
  Attributes:
      email (str): User's email address.
      password (str): Plain text password for authentication.
  """
  username: str
  password : str