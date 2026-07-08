import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load env variables using an absolute path relative to this file
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/echomind.db")

# Ensure sqlite relative path maps to the correct folder relative to project root
if DATABASE_URL.startswith("sqlite:///./"):
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(backend_dir)
    db_relative_path = DATABASE_URL.replace("sqlite:///./", "")
    db_absolute_path = os.path.join(root_dir, db_relative_path)
    os.makedirs(os.path.dirname(db_absolute_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_absolute_path}"
else:
    # Ensure directory is created for local sqlite URLs without ./ prefix
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    # Import models here to register them with Base
    from backend.models.event import Event
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
