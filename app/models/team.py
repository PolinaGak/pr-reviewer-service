from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class Team(Base):
    __tablename__ = "teams"

    team_name = Column(String, primary_key=True, index=True)
    members = relationship("User", back_populates="team", cascade="all, delete-orphan")