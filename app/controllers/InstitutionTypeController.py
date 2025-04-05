from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import InstitutionType, InstitutionTypeCreate

def get_all(session: Session):
    """
    Retrieve all institution types from the database.
    
    Args:
        session (Session): Database session for operations.
    
    Returns:
        List[InstitutionType]: List of all institution type objects.
    """
    return session.exec(select(InstitutionType)).all()

def get_by_id(id: int, session: Session):
    """
    Get a single institution type by its ID.
    
    Args:
        id (int): The ID of the institution type to retrieve.
        session (Session): Database session for operations.
    
    Returns:
        InstitutionType: The requested institution type.
    
    Raises:
        HTTPException: 404 if institution type is not found.
    """
    institution = session.get(InstitutionType, id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution type not found"
        )
    return institution

def create_institution_type(institution_type: InstitutionTypeCreate, session: Session):
    """
    Create a new institution type.
    
    Args:
        institution_type (InstitutionTypeCreate): Institution type data to create.
        session (Session): Database session for operations.
    
    Returns:
        InstitutionType: The newly created institution type.
    
    Raises:
        HTTPException: 400 if name is empty.
    """
    # Validación del nombre
    if not institution_type.institution_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution type name cannot be empty"
        )
    
    db_institution = InstitutionType.model_validate(institution_type)
    session.add(db_institution)
    session.commit()
    session.refresh(db_institution)
    return db_institution

def delete_institution_type(id: int, session: Session):
    """
    Delete an institution type by ID.
    
    Args:
        id (int): The ID of the institution type to delete.
        session (Session): Database session for operations.
    
    Returns:
        dict: Confirmation message with deletion result.
    
    Raises:
        HTTPException: 404 if institution type is not found.
    """
    institution = session.get(InstitutionType, id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution type not found"
        )
    
    session.delete(institution)
    session.commit()
    return {"message": f"Institution type {id} deleted"}

def update_institution_type(id: int, institution_type: InstitutionTypeCreate, session: Session):
    """
    Update an existing institution type.
    
    Args:
        id (int): The ID of the institution type to update.
        institution_type (InstitutionTypeCreate): New data for the institution type.
        session (Session): Database session for operations.
    
    Returns:
        InstitutionType: The updated institution type object.
    
    Raises:
        HTTPException: 400 if name is empty.
        HTTPException: 404 if institution type is not found.
    """
    if not institution_type.institution_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution type name cannot be empty"
        )
    
    db_institution = session.get(InstitutionType, id)
    if not db_institution:
        raise HTTPException(status_code=404, detail="Institution type not found")
    
    institution_data = institution_type.model_dump(exclude_unset=True)
    for key, value in institution_data.items():
        setattr(db_institution, key, value)
    
    session.add(db_institution)
    session.commit()
    session.refresh(db_institution)
    return db_institution