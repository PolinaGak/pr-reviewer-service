from __future__ import annotations

from pydantic import BaseModel
from typing import List


class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool


class TeamCreate(BaseModel):
    team_name: str
    members: List[TeamMember]


class TeamResponse(BaseModel):
    team_name: str
    members: List[TeamMember]

    model_config = dict(from_attributes=True)
