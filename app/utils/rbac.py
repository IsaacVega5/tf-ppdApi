from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.utils.auth import get_current_user
from app.models.User import User
from app.models import UserInstitution

from sqlmodel import Session, select
from app.db import get_session


def verify_institution_role(
    institution_id: str,
    required_roles: list[str],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    if current_user.is_admin:
        return True

    institution_memberships = session.exec(
        select(UserInstitution)
        .where(UserInstitution.id_user == current_user.id_user)
        .where(UserInstitution.id_institution == institution_id)
    ).all()

    if not institution_memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't have access to resources of this institution."
        )
    
    if len(institution_memberships) > 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multiple memberships found for user in institution"
        )
    
    institution_membership = institution_memberships[0]
    
    if institution_membership.user_rol.user_rol_name not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role for this action in this institution."
        )
    
    return True