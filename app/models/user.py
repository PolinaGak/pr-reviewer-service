from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    team_name = Column(String, ForeignKey("teams.team_name"), nullable=False)

    team = relationship("Team", back_populates="members")