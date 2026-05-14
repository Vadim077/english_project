from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    level = Column(String, default="A1") # A1, A2, B1, B2, C1, C2

    scenarios = relationship("Scenario", back_populates="owner")

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String) # Описание ситуации на русском
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="scenarios")
    messages = relationship("Message", back_populates="scenario")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    role = Column(String) # user или ai
    text = Column(Text)
    corrections = Column(Text, nullable=True) # Разбор ошибок от ИИ

    scenario = relationship("Scenario", back_populates="messages")