import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base


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
    merged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
