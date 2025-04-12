from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.UserRol import UserRol


def get_all(session: Session):
    return session.exec(select(UserRol).all())

def get_id_by_name(name: str, session: Session):
    statement = select(UserRol).where(UserRol.user_rol_name == name)
    return session.exec(statement).first().id_user_rol
