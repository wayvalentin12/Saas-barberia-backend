from fastapi import FastAPI
from routers import user, appoiments

app = FastAPI()
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(appoiments.router, prefix="/appointments", tags=["Appointments"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de la Barbería"}


