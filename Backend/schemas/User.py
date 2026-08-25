from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):

    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):

    email: str
    password: str

class UserUpdate(BaseModel):
        name: str
        email: str