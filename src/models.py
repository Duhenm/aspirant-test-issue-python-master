from pydantic import BaseModel

"""
Добавлено ограничение по возрасту 
"""
class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=2)
    surname: str = Field(min_length=2)
    age: int = Field(gt=0, le=1000)


class UserModel(BaseModel):
    id: int
    name: str
    surname: str
    age: int

    class Config:
        orm_mode = True
