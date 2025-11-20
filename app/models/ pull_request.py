from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base
import enum
from datetime import datetime

class PRStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"

class PullRequest(Base):
    __tablename__ = "pull_requests"

    pull_request_id = Column(String, primary_key=True, index=True)
    pull_request_name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(PRStatus), default=PRStatus.OPEN, nullable=False)
    assigned_reviewers = Column(ARRAY(String), default=[], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    merged_at = Column(DateTime, nullable=True)