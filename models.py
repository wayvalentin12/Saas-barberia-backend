from database import base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class Negocio(base):
    __tablename__ = "negocios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)

class User(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(300), nullable=False)
    role = Column(String(20), nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=False)

class Barber(base):
    __tablename__ = "barbers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(300), nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=False)

class Appointment(base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    username= Column(String(50), nullable=False)
    date_time = Column(DateTime, nullable=False)
    service = Column(String(100), nullable=False)
    barber_id = Column(Integer, ForeignKey("barbers.id"), nullable=False)
    negocio_id = Column(Integer, ForeignKey("negocios.id"), nullable=False)