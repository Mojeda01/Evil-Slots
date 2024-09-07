from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)  # Make sure this line is present
    password_hash = Column(String)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    total_spins = Column(Integer, default=0)
    total_winnings = Column(Float, default=0.0)
    
    sessions = relationship("GameSession", back_populates="player")
    transactions = relationship("Transaction", back_populates="player")

class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    initial_balance = Column(Float)
    final_balance = Column(Float)
    
    player = relationship("Player", back_populates="sessions")
    game_results = relationship("GameResult", back_populates="session")

class GameResult(Base):
    __tablename__ = "game_results"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"))
    spin_number = Column(Integer)
    bet_amount = Column(Float)
    outcome = Column(String)
    winnings = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("GameSession", back_populates="game_results")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    amount = Column(Float)
    type = Column(String)  # e.g., "deposit", "withdrawal", "bet", "win"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="transactions")

# You might want to add more models like Jackpot or BonusGame if needed
