from fastapi import APIRouter, HTTPException

from backend.schemas.auth import AuthOut, LoginIn, RegistroIn
from backend.services import auth as auth_service

router = APIRouter()


@router.post("/registro", response_model=AuthOut, status_code=201)
def registro(payload: RegistroIn) -> AuthOut:
    try:
        print(payload)
        return auth_service.registrar(payload)
    except auth_service.DniYaRegistrado:
        raise HTTPException(status_code=409, detail="El DNI ya está registrado")


@router.post("/login", response_model=AuthOut, status_code=200)
def login(payload: LoginIn) -> AuthOut:
    try:
        return auth_service.autenticar(payload)
    except auth_service.CredencialesInvalidas:
        raise HTTPException(status_code=401, detail="DNI o contraseña incorrectos")
