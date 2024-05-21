from pydantic import BaseModel


class UserDto(BaseModel):
    name: str
    email: str
