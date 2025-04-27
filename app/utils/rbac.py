from typing import List, Annotated
from fastapi import Depends, HTTPException, status

from app.utils.auth import get_current_user
from app.models.User import User
from app.models import UserInstitution, Role

from sqlmodel import Session, select
from app.db import get_session


def verify_institution_role(
    institution_ids: List[str],
    required_role: Role,
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
    
    for membership in memberships:
        if membership.role < required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User can't execute this action for institution: {membership.id_institution}"
            )
    
    return True
