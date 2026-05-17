from fastapi import FastAPI
from routers import user, appoiments, login, register

app = FastAPI()
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(appoiments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(login.router, prefix="/login", tags=["Login"])
app.include_router(register.router, prefix="/register", tags=["Register"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de la Barbería"}


