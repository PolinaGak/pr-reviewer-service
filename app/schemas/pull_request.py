from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus

    model_config = dict(from_attributes=True)


class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestResponse(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str]
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    merged_at: Optional[datetime] = Field(None, alias="mergedAt")

    model_config = dict(from_attributes=True)


class ReassignRequest(BaseModel):
    pull_request_id: str
    old_user_id: str


class ReassignResponse(BaseModel):
    pr: PullRequestResponse
    replaced_by: str
