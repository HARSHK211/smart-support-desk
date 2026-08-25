from sqlalchemy import Column, Integer, String
from database.sql_database import Base

class User(Base):

    __tablename__ = "users"
    customer_code = Column(
        String(20),
        unique=True,
        nullable=False
    )
    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password = Column(String(100), nullable=False)

    role = Column(String(20), default="customer")