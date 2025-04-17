import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

engine = None

def init_db():
    global engine
    db = os.getenv("DATABASE")

    if db == "sqlite": # Use SQLite for testing
        db_url = "sqlite:///:memory:"
    else:
        db_name = os.getenv("DATABASE_NAME")
        db_host = os.getenv("DATABASE_HOST")
        db_user = os.getenv("DATABASE_USER")
        db_password = os.getenv("DATABASE_PASSWORD")
        db_sslmode = os.getenv("DATABASE_SSLMODE")
        db_url = f"{db}://{db_user}:{db_password}@{db_host}/{db_name}?sslmode={db_sslmode}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db == "sqlite" else {})
    SQLModel.metadata.create_all(engine, checkfirst=True)


def get_session():
    if engine is None:
        raise RuntimeError("DB engine not initialized. Call init_db() first.")
    with Session(engine) as session:
        yield session