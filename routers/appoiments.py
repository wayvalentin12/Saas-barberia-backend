from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Appointment    
from schemes import AppointmentCreate

router = APIRouter()

@router.get("/", response_model=list[AppointmentCreate])
async def read_appointments(db: Session = Depends(get_db)):
    Appointments = db.query(Appointment).all()
    return Appointments
@router.post("/", response_model=AppointmentCreate)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == appointment.barber_id).first()
    if not user or user.role != "barbero":
        raise HTTPException(status_code=400, detail="Invalid barber ID")

    new_appointment = Appointment(
        username=appointment.username,
        date_time=appointment.date_time,
        service=appointment.service,
        barber_id=appointment.barber_id
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment