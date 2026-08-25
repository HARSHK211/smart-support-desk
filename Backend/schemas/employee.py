from pydantic import BaseModel, EmailStr


class CreateEmployee(BaseModel):
    name: str
    email: EmailStr
    password: str

class EmployeeLogin(BaseModel):

    email: EmailStr
    password: str

class EmployeeUpdate(BaseModel):
    name: str
    email: EmailStr


class EmpCreateTicket(BaseModel):

    customer_id: int

    title: str

    description: str

    team_id: int

    priority: str