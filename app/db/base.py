from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
