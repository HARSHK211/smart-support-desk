from pydantic import BaseModel


class AgentSupportCreate(BaseModel):
    title: str
    description: str
    priority: str
    team_id: int