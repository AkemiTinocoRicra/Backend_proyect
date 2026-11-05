from datetime import datetime, timedelta, timezone

import jwt

from backend.config import settings
from backend.repositories import estudiantes as repo
from backend.schemas.auth import AuthOut, LoginIn, RegistroIn

ALGORITMO = "HS256"


class DniYaRegistrado(Exception):
    pass


class CredencialesInvalidas(Exception):
    pass


def _firmar_token(id_estudiante: int, dni: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_estudiante),
        "dni": dni,
        "role": "estudiante",
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_expire_min),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITMO)


def registrar(datos: RegistroIn) -> AuthOut:
    if repo.find_by_dni(datos.dni) is not None:
        raise DniYaRegistrado()

    id_estudiante = repo.insert(
        dni=datos.dni,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        fecha_nacimiento=datos.fecha_nacimiento,
        contrasena=datos.contrasena,
       
    )

    token = _firmar_token(id_estudiante, datos.dni)
    return AuthOut(token=token, dni=datos.dni)


def autenticar(datos: LoginIn) -> AuthOut:
    estudiante = repo.find_by_dni(datos.dni)
    if (
        estudiante is None
        or estudiante["contrasena"] != datos.contrasena
        or estudiante["estado"] != "AC"
    ):
        raise CredencialesInvalidas()

    token = _firmar_token(estudiante["id_estudiante"], datos.dni)
    return AuthOut(token=token, dni=datos.dni)
