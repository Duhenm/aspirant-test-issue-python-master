from pydantic import BaseModel, Field
from datetime import datetime

"""
Добавлено ограничение по возрасту 
"""


class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=2)
    surname: str = Field(min_length=2)
    age: int = Field(gt=0, le=1000)


class CityModal(BaseModel):
    name: str = Field(min_length=2)


class PicnicRegistrationModal(BaseModel):
    user_id: int
    picnic_id: int

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    id: int
    name: str
    surname: str
    age: int

    class Config:
        orm_mode = True


class PicnicModal(BaseModel):
    city_id: int
    time: datetime

    class Config:
        orm_mode = True
