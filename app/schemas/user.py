from __future__ import annotations

from pydantic import BaseModel
from typing import List

from .pull_request import PullRequestShort


class UserResponse(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool

    model_config = dict(from_attributes=True)


class UserSetActive(BaseModel):
    user_id: str
    is_active: bool


class UserReviewResponse(BaseModel):
    user_id: str
    pull_requests: List[PullRequestShort]

    model_config = dict(from_attributes=True)
