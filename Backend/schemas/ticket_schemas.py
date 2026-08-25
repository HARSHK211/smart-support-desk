from pydantic import BaseModel


class CreateTicket(BaseModel):

    customer_id: int

    title: str

    description: str

    team_id: int

    priority: str