from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Appointment    
from schemes import AppointmentCreate
from auth import get_current_user

router = APIRouter()

@router.get("/todas-las-citas/", response_model=list[AppointmentCreate])
async def read_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    Appointments = db.query(Appointment).filter(Appointment.negocio_id == current_user.negocio_id).all()
    return Appointments
@router.post("/crear-citas/", response_model=AppointmentCreate)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role == "barbero":
        raise HTTPException(status_code=400, detail="No estas autorizado para crear citas")

    new_appointment = Appointment(
        username=appointment.username,
        date_time=appointment.date_time,
        service=appointment.service,
        barber_id=appointment.barber_id,
        negocio_id=current_user.negocio_id
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment