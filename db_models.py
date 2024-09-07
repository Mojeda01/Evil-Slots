from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base  # Updated import

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime)

# Add more models as needed
