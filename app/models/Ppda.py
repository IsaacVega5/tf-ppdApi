from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING: from app.models import Action, Institution

class PpdaBase(SQLModel):
    """Base model class for PPDA (Plan de Prevención y Descontaminación Atmosférica) containing common attributes.
    
    Attributes:
        id_institution (Optional[str]): Foreign key referencing the institution this PPDA belongs to
    """
    id_institution: Optional[str] = Field(default=None, foreign_key="institution.id_institution")

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