import re
from datetime import date

from pydantic import BaseModel, Field, field_validator

CONTRASENA_PATTERN = re.compile(r"^\d{4}$")
ESTADOS_VALIDOS = ("AC", "IN")


class EstudianteOut(BaseModel):
    id_estudiante: int
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    id_grado: int
    estado: str
    cantidad_copas: int


class EstudianteUpdateIn(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None
    contrasena: str | None = None
    id_grado: int | None = Field(default=None, ge=1, le=6)
    estado: str | None = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str | None) -> str | None:
        if valor is not None and valor not in ESTADOS_VALIDOS:
            raise ValueError("El estado debe ser 'AC' o 'IN'")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str | None) -> str | None:
        if valor is not None and not CONTRASENA_PATTERN.match(valor):
            raise ValueError("La contraseña debe tener exactamente 4 dígitos numéricos")
        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_texto_no_vacio(cls, valor: str | None) -> str | None:
        if valor is not None and not valor.strip():
            raise ValueError("No puede estar vacío")
        return valor.strip() if valor is not None else valor
