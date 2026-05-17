from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  
from database import get_db
from models import User, Negocio, Barber
from schemes import NegocioCreate, UserDB, UserResponse, NegocioResponse, BarberCreate, BarberResponse
from auth import hash_password
from sqlalchemy.exc import IntegrityError


router = APIRouter()

@router.post("/usuario/", response_model=UserResponse, status_code=201)
async def register_user(payload: UserDB, db: Session = Depends(get_db)):
    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role,
        negocio_id=payload.negocio_id
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    return user

@router.post("/negocio/", response_model=NegocioResponse, status_code=201)
async def register_negocio(negocio: NegocioCreate, db: Session = Depends(get_db)):
    negocio_check = db.query(Negocio).filter(Negocio.name == negocio.name).first()
    if negocio_check:
        raise HTTPException(status_code=400, detail="El negocio ya existe")
    new_negocio = Negocio(name=negocio.name)
    db.add(new_negocio)
    db.commit()
    db.refresh(new_negocio)
    return new_negocio

@router.post("/barbero/", response_model=BarberResponse, status_code=201)
async def register_barber(payload: BarberCreate, db: Session = Depends(get_db)):
    barber = Barber(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        negocio_id=payload.negocio_id
    )
    db.add(barber)
    try:
        db.commit()
        db.refresh(barber)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    return barber