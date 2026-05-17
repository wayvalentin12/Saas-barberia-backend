from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    name: str
    email: str
    role: str

class UserDB(UserResponse):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserResponse(UserResponse):
    id: int

    class Config:
        orm_mode = True

class AppointmentCreate(BaseModel):
    username: str
    date_time: datetime
    service: str
    barber_id: int
