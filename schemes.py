from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NegocioCreate(BaseModel):
    name: str

class NegocioResponse(NegocioCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class BarberCreate(BaseModel):
    name: str
    email: str
    password: str
    negocio_id: int

class BarberResponse(BarberCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class UserBase(BaseModel):
    name: str
    email: str
    role: str
    negocio_id: int

class UserDB(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    negocio_id: Optional[int] = None

class UserResponse(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class AppointmentCreate(BaseModel):
    username: str
    date_time: datetime
    service: str
    barber_id: int

    model_config = {
        "from_attributes": True
    }
