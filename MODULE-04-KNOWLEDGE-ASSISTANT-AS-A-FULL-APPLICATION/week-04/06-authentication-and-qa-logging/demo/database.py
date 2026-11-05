"""MySQL connection via SQLAlchemy.

Reads DATABASE_URL from .env.  Default: mysql+pymysql://root:@localhost/novanet_hr_app
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:@localhost/novanet_hr_app"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Yield a database session for FastAPI Depends()."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
