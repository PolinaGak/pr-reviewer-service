from pydantic import BaseModel
from typing import List


class UserStats(BaseModel):
    user_id: str
    assigned_count: int


class PRStatusStats(BaseModel):
    status: str
    count: int


class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    total_prs: int
    prs_by_status: List[PRStatusStats]
    top_reviewers: List[UserStats]
