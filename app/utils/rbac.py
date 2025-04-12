from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.utils.auth import get_current_user
from app.models.User import User
from app.models import UserInstitution
from app.controllers import UserRolController

from sqlmodel import Session, select
from app.db import get_session


def verify_institution_role(
    institution_id: str,
    required_role: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    if current_user.is_admin:
        return True

    institution_membership = session.exec(
        select(UserInstitution)
        .where(UserInstitution.id_user == current_user.id_user)
        .where(UserInstitution.id_institution == institution_id)
    ).first()

    if not institution_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User can't access to resources of this institution."
        )
    
    required_level_access = UserRolController.get_id_by_name(required_role, session)
    membership_level_access = UserRolController.get_id_by_name(
        name=institution_membership.user_rol.user_rol_name,
        session=session
    )
    
    if membership_level_access < required_level_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User can't execute this action for this institution."
        )
    
    return True