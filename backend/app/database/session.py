# app/database/session.py

from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///app/database/sample.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)
