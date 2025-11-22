from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import ConfigDict

from pydantic import BaseModel, Field


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus

    model_config = ConfigDict(from_attributes=True)


class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str]
    merged_at: Optional[datetime] = Field(None, alias="mergedAt")
    created_at: Optional[datetime] = Field(None, alias="createdAt")


class ReassignRequest(BaseModel):
    pull_request_id: str
    old_user_id: str


class ReassignResponse(BaseModel):
    pr: PullRequestResponse
    replaced_by: str
