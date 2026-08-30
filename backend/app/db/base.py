from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base Declarative class for SQLAlchemy models.
    Application tables will inherit from this Base in subsequent implementation steps.
    """
    pass
