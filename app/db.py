import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

db = os.getenv("DATABASE")
db_name = os.getenv("DATABASE_NAME")
db_host = os.getenv("DATABASE_HOST")
db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_sslmode = os.getenv("DATABASE_SSLMODE")
DB_URL = f"{db}://{db_user}:{db_password}@{db_host}/{db_name}?sslmode={db_sslmode}"

engine = create_engine(DB_URL)
SQLModel.metadata.create_all(engine, checkfirst=True)

def get_session():
  with Session(engine) as session:
    yield session 