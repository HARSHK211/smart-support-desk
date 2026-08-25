from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.sql_database import Base


class AgentSupportTicket(Base):
    __tablename__ = "agent_support_tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_number = Column(
        String(30),
        unique=True,
        nullable=False
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )
    
    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    assigned_admin = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    priority = Column(
        String(20),
        nullable=False
    )

    status = Column(
        String(30),
        default="Open"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    # Relationships

    employee = relationship(
        "Employee",
        foreign_keys=[employee_id]
    )

    admin = relationship(
        "Employee",
        foreign_keys=[assigned_admin]
    )