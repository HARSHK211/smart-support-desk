from sqlalchemy import Column, Integer, String
from database.sql_database import Base


class Team(Base):

    __tablename__ = "teams"

    id = Column(
        Integer,
        primary_key=True
    )

    team_name = Column(
        String(100),
        unique=True,
        nullable=False
    )