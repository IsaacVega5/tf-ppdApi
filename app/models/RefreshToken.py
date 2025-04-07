
import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import field_validator
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import User

class RefreshTokenBase(SQLModel):
    id_user: str = Field(default=None, foreign_key="user.id_user")
    token_hash: str = Field(nullable=False)
    created_at: int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    updated_at: int = Field(nullable=True, default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()), sa_column_kwargs={"onupdate": int(datetime.datetime.now(datetime.timezone.utc).timestamp())})
    expires_at: int = Field(nullable=False)
    used: bool = Field(default=False)
    revoked: bool = Field(default=False)

class RefreshToken(RefreshTokenBase, table=True):
    __tablename__ = "refresh_token"

    id_token: Optional[str] = Field(nullable=False, primary_key=True, unique=True)
    
    user : Optional["User"] = Relationship(back_populates="refresh_token")

# class RefreshTokenCreate(RefreshTokenBase):
#     ...

# class RefreshTokenUpdate(RefreshTokenBase):
#     ...
