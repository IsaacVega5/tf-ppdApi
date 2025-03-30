import sqlmodel as sql
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models import Institution, InstitutionCreate, InstitutionUpdate

async def get_all(session : sql.Session):
  statement = sql.select(Institution)
  institutions = session.exec(statement).all()
  return institutions

async def get_by_id(id:str, session : sql.Session):
  statement = sql.select(Institution).\
    where(Institution.id_institution == id)
  institution = session.exec(statement).first()
  return institution

async def create_institution(institution: InstitutionCreate, session: sql.Session):
    # Verificar si ya existe una institución con el mismo nombre y tipo
    from app.models import InstitutionType  # Importar aquí para evitar circular imports
    try:
        # Verificar si ya existe una institución con el mismo nombre y tipo
        existing = session.exec(
            sql.select(Institution).where(
                Institution.institution_name == institution.institution_name,
                Institution.id_institution_type == institution.id_institution_type
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An institution with this name and type already exists"
            )
        
        # Verificar si el tipo de institución existe
        institution_type = session.get(InstitutionType, institution.id_institution_type)
        if not institution_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution type with ID {institution.id_institution_type} not found"
            )
        
        new_institution = Institution.model_validate(institution)
        session.add(new_institution)
        session.commit()
        session.refresh(new_institution)
        
        return new_institution
        
    except IntegrityError as e:
        session.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An institution with this name and type already exists"
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        ) from e

async def delete_institution(id: str, session: sql.Session):
    # Verificar si la institución existe
    institution = await get_by_id(id, session)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID {id} not found"
        )
    
    # Verificar si hay usuarios asociados.
    if hasattr(institution, 'user_institution_institution') and institution.user_institution_institution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete institution with associated users"
        )
    
    try:
        statement = sql.delete(Institution).where(Institution.id_institution == id)
        session.exec(statement)
        session.commit()
        return {"message": f"Institution {id} deleted successfully", "deleted_institution": institution}
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting institution: {str(e)}"
        ) from e


async def update_institution(id: str, institution: InstitutionUpdate, session: sql.Session):
    # Verificar si la institución existe
    existing = await get_by_id(id, session)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID {id} not found"
        )
    
    changes = institution.model_dump(exclude_unset=True)
    if not changes:
        return existing
    
    # Validar si se actualiza el nombre o tipo
    if 'institution_name' in changes or 'id_institution_type' in changes:
        new_name = changes.get('institution_name', existing.institution_name)
        new_type = changes.get('id_institution_type', existing.id_institution_type)
        
        # Verificar si ya existe otra institución con el mismo nombre y tipo
        duplicate = session.exec(
            sql.select(Institution).where(
                Institution.institution_name == new_name,
                Institution.id_institution_type == new_type,
                Institution.id_institution != id  # Excluir la actual
            )
        ).first()
        
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An institution with this name and type already exists"
            )
    
    # Validar tipo de institución si se actualiza
    if 'id_institution_type' in changes:
        from app.models import InstitutionType
        institution_type = session.get(InstitutionType, changes['id_institution_type'])
        if not institution_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution type with ID {changes['id_institution_type']} not found"
            )
    
    try:
        statement = sql.update(Institution).\
            where(Institution.id_institution == id).\
            values(changes)
        session.exec(statement)
        session.commit()
        session.refresh(existing)
        return await get_by_id(id, session)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error updating institution: {str(e)}"
        ) from e