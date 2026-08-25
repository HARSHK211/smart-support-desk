from typing import Optional
from pydantic import BaseModel

class TeamCreate(BaseModel):
    team_name: str
    description: Optional[str] = None