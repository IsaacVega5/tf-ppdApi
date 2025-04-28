from fastapi import HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from app.models.Kpi import Kpi

async def create_kpi(kpi: Kpi, session: Session) -> Kpi:
    """
    Create a new KPI (Key Performance Indicator).

    Args:
        kpi (Kpi): KPI data to create.
        session (Session): Database session.

    Returns:
        Kpi: The newly created KPI object.
    """
    session.add(kpi)
    session.commit()
    session.refresh(kpi)
    return kpi

async def get_kpi_by_id(id_kpi: str, session: Session) -> Kpi:
    """
    Get a KPI by its unique identifier.

    Args:
        id_kpi (str): The unique KPI ID.
        session (Session): Database session.

    Returns:
        Kpi: The KPI object if found.

    Raises:
        HTTPException: 404 if KPI not found.
    """
    kpi = session.get(Kpi, id_kpi)
    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    return kpi

async def get_all_kpis(session: Session) -> List[Kpi]:
    """
    Get all KPIs in the database.

    Args:
        session (Session): Database session.

    Returns:
        List[Kpi]: List of all KPIs.
    """
    statement = select(Kpi)
    return session.exec(statement).all()

async def update_kpi(id_kpi: str, kpi_data: Kpi, session: Session) -> Kpi:
    """
    Update an existing KPI by its ID.

    Args:
        id_kpi (str): The unique KPI ID.
        kpi_data (Kpi): New data for the KPI.
        session (Session): Database session.

    Returns:
        Kpi: The updated KPI object.

    Raises:
        HTTPException: 404 if KPI not found.
    """
    kpi = session.get(Kpi, id_kpi)
    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    for key, value in kpi_data.model_dump(exclude_unset=True).items():
        setattr(kpi, key, value)
    session.add(kpi)
    session.commit()
    session.refresh(kpi)
    return kpi

async def delete_kpi(id_kpi: str, session: Session) -> dict:
    """
    Delete a KPI by its ID.

    Args:
        id_kpi (str): The unique KPI ID.
        session (Session): Database session.

    Returns:
        dict: Confirmation message with deleted KPI ID.

    Raises:
        HTTPException: 404 if KPI not found.
    """
    kpi = session.get(Kpi, id_kpi)
    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    session.delete(kpi)
    session.commit()
    return {"detail": "KPI deleted", "id": id_kpi}

async def get_kpis_by_action(id_action: str, session: Session) -> List[Kpi]:
    """
    Get all KPIs associated with a specific action.

    Args:
        id_action (str): The action ID.
        session (Session): Database session.

    Returns:
        List[Kpi]: List of KPIs related to the action.
    """
    statement = select(Kpi).where(Kpi.id_action == id_action)
    return session.exec(statement).all()
