from sqlmodel import Session

from app.models.User import UserCreate, User


def create_user(user: UserCreate, session : Session):
  new_user = User.model_validate(user)
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user
  