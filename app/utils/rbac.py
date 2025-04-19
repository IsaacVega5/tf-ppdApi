from typing import List, Annotated
from fastapi import Depends, HTTPException, status

from app.utils.auth import get_current_user
from app.models.User import User
from app.models import UserInstitution
from app.controllers import UserRolController

from sqlmodel import Session, select
from app.db import get_session


def get_id_by_name(name: str, session: Session):
    user_rol = UserRolController.get_by_name(name=name, session=session)
    if user_rol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User role '{name}' not found")
    return user_rol.id_user_rol

def verify_institution_role(
    institution_ids: List[str],
    required_role: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    if not institution_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="institution_ids cannot be empty"
        )

    if current_user.is_admin:
        return True

    memberships = session.exec(
        select(UserInstitution)
        .where(UserInstitution.id_user == current_user.id_user)
        .where(UserInstitution.id_institution.in_(institution_ids))
    ).all()

    if len(memberships) < len(institution_ids):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User in not member of all required institutions"
        )
    
    required_access_level = get_id_by_name(required_role, session)
    
    for membership in memberships:
        membership_access_level = get_id_by_name(
            name=membership.user_rol.user_rol_name,
            session=session
        )
        
        if membership_access_level < required_access_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User can't execute this action for institution: {membership.id_institution}"
            )
    
    return True
