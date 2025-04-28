from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone
from app.models.PpdaStatus import PpdaStatus
from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum

if TYPE_CHECKING: from app.models import Action, Institution


class PpdaBase(SQLModel):
    """Base model class for PPDA (Plan de Prevención y Descontaminación Atmosférica) containing common attributes.
    
    Attributes:
        id_institution (Optional[str]): Foreign key referencing the institution this PPDA belongs to
    """
    id_institution: Optional[str] = Field(default=None, foreign_key="institution.id_institution")
    
    name: str = Field(..., description="Name of the PPDA")
    description: Optional[str] = Field(None, description="Detailed description")
    region: Optional[str] = Field(None, description="Region where it applies")
    municipality: Optional[str] = Field(None, description="Municipality where it applies")
    geographic_scope: Optional[str] = Field(None, description="Geographic scope")
    start_date: Optional[int] = Field(None, description="Start date [unix timestamp]")
    end_date: Optional[int] = Field(None, description="End date [unix timestamp]")
    status: Optional[str] = Field(None, description="Current PPDA status in it's life cycle")
    created_at : int = Field(
        nullable=True,
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp()),
        description="Record creation timestamp"
    )
    updated_at : int = Field(
        nullable=True,
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp()),
        sa_column_kwargs={"onupdate": int(datetime.now(timezone.utc).timestamp())},
        description="Record last‐update timestamp"
    )


class Ppda(PpdaBase, table=True):
    """Database model for PPDA (Plan de Prevención y Descontaminación Atmosférica).
    
    Inherits from PpdaBase and implements the database table structure.
    
    Attributes:
        id_ppda (Optional[str]): Unique identifier for the PPDA, auto-generated UUID
        actions (list[Action]): List of actions associated with this PPDA
        institution (Optional[Institution]): Relationship to the institution responsible for this PPDA
    """
    __tablename__ = "ppda"
    id_ppda: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True)
    
    actions : list["Action"] = Relationship(back_populates="ppda")
    institution : Optional["Institution"] = Relationship(back_populates="ppda_list")

class PpdaCreate(PpdaBase):
    """Model for creating a new PPDA (Plan de Prevención y Descontaminación Atmosférica).
    
    Inherits from PpdaBase and is used for creating new PPDA instances.
    
    Attributes:
        id_institution (str): Foreign key referencing the institution this PPDA belongs to
    """
    id_institution: Optional[str]
    name: Optional[str] = None

class PpdaUpdate(PpdaBase):
    """Model for updating an existing PPDA (Plan de Prevención y Descontaminación Atmosférica).
    
    Inherits from PpdaBase and is used for updating existing PPDA instances.
    
    Attributes:
        id_institution (str): Foreign key referencing the institution this PPDA belongs to
    """
    id_institution: Optional[str] = None
    id_institution: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    municipality: Optional[str] = None
    geographic_scope: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None
    status: Optional[str] = None