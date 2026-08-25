from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import Enum
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from database.sql_database import Base


class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    ticket_number = Column(String(20), unique=True)

    title = Column(String(255))

    description = Column(Text)

    customer_id = Column(Integer, ForeignKey("users.id"))

    team_id = Column(Integer, ForeignKey("teams.id"))

    assigned_to = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    priority = Column(
        Enum(
            "Low",
            "Medium",
            "High",
            "Critical",
            name="priority_enum"
        ),
        default="Medium"
    )

    status = Column(
        Enum(
            "Open",
            "In Progress",
            "Resolved",
            "Closed",
            name="status_enum"
        ),
        default="Open"
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