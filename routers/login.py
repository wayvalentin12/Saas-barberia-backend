from models import User, Barber
from auth import verify_password, create_access_token
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/")
async def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscar primero en la tabla de usuarios normales / administradores
    db_user = db.query(User).filter(User.email == user.username).first()
    if db_user:
        if not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token({"email": db_user.email, "role": db_user.role})
        return {"access_token": access_token, "token_type": "bearer"}
    
    # 2. Si no se encuentra, buscar en la tabla de barberos
    db_barber = db.query(Barber).filter(Barber.email == user.username).first()
    if db_barber:
        if not verify_password(user.password, db_barber.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token({"email": db_barber.email, "role": db_barber.role})
        return {"access_token": access_token, "token_type": "bearer"}
        
    raise HTTPException(status_code=401, detail="Invalid credentials")


