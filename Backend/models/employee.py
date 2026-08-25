from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime
)

from sqlalchemy.sql import func

from database.sql_database import Base


class Employee(Base):

    __tablename__ = "employees"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    employee_id = Column(
        String(20),
        unique=True,
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    # Default role after registration
    role = Column(
        String(30),
        nullable=False,
        default="employee"
    )

    # Assigned later by Admin
    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=True
    )

    # Admin activates account after verification
    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )