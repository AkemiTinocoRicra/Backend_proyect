from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import settings

ALGORITMO = "HS256"

_bearer = HTTPBearer(auto_error=False)


def requiere_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        return jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[ALGORITMO],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
