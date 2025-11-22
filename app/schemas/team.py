from __future__ import annotations

from typing import List
from pydantic import ConfigDict

from pydantic import BaseModel


class TeamMember(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    username: str
    is_active: bool


class TeamCreate(BaseModel):
    team_name: str
    members: List[TeamMember]


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_name: str
    members: List[TeamMember]
