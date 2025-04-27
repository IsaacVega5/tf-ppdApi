from fastapi import HTTPException, status
from app.models.DeadLine import DeadLine, DeadLineBase
from sqlmodel import select, Session
from datetime import datetime

async def get_all(session: Session):
    """
    Retrieve all deadlines from the database.
    Args:
        session (Session): The database session.
    Returns:
        List[DeadLine]: A list of all deadline objects.
    """
    statement = select(DeadLine)
    return session.exec(statement).all()

async def get_by_id(id: str, session: Session):
    """
    Retrieve a deadline by its ID.
    Args:
        id (str): The UUID of the deadline to retrieve.
        session (Session): The database session.
    Returns:
        DeadLine: The requested deadline object if found.
    Raises:
        HTTPException: If the deadline is not found (404).
    """
    statement = select(DeadLine).where(DeadLine.id_deadline == id)
    deadline = session.exec(statement).first()
    if not deadline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    return deadline

async def create_deadline(deadline_data, session: Session):
    """
    Create a new deadline in the database.
    Args:
        deadline_data: Data for the new deadline (should be compatible with DeadLine model).
        session (Session): The database session.
    Returns:
        DeadLine: The newly created deadline object.
    """
    deadline = DeadLine(**deadline_data.model_dump()) if hasattr(deadline_data, 'model_dump') else DeadLine(**dict(deadline_data))
    session.add(deadline)
    session.commit()
    session.refresh(deadline)
    return deadline

async def update_deadline(id: str, deadline_data, session: Session):
    """
    Update an existing deadline by its ID.
    Args:
        id (str): The UUID of the deadline to update.
        deadline_data: Partial or full data to update (should be compatible with DeadLine model).
        session (Session): The database session.
    Returns:
        DeadLine: The updated deadline object.
    Raises:
        HTTPException: If the deadline is not found (404).
    """
    statement = select(DeadLine).where(DeadLine.id_deadline == id)
    deadline = session.exec(statement).first()
    if not deadline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    for key, value in (deadline_data.model_dump().items() if hasattr(deadline_data, 'model_dump') else dict(deadline_data).items()):
        setattr(deadline, key, value)
    session.add(deadline)
    session.commit()
    session.refresh(deadline)
    return deadline

async def delete_deadline(id: str, session: Session):
    """
    Delete a deadline by its ID.
    Args:
        id (str): The UUID of the deadline to delete.
        session (Session): The database session.
    Returns:
        dict: Confirmation message and deleted deadline ID.
    Raises:
        HTTPException: If the deadline is not found (404).
    """
    statement = select(DeadLine).where(DeadLine.id_deadline == id)
    deadline = session.exec(statement).first()
    if not deadline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    session.delete(deadline)
    session.commit()
    return {"detail": "Deadline deleted", "id": id}

async def get_by_action(id_action: str, session: Session):
    statement = select(DeadLine).where(DeadLine.id_action == id_action)
    return session.exec(statement).all()

async def get_by_date_range(from_date: datetime, to_date: datetime, session: Session):
    statement = select(DeadLine).where(
        (DeadLine.deadline_date >= from_date) & (DeadLine.deadline_date <= to_date)
    )
    return session.exec(statement).all()

async def get_active(session: Session):
    now = datetime.now()
    statement = select(DeadLine).where(DeadLine.deadline_date >= now)
    return session.exec(statement).all()

async def get_inactive(session: Session):
    now = datetime.now()
    statement = select(DeadLine).where(DeadLine.deadline_date < now)
    return session.exec(statement).all()
