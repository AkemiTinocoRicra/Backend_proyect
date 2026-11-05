from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.apis import auth, estudiantes
from backend.config import settings

app = FastAPI(title="API de Booki")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(estudiantes.router, prefix="/api/estudiantes", tags=["estudiantes"])
