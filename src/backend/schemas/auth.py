import re
from datetime import date

from pydantic import BaseModel, field_validator

DNI_PATTERN = re.compile(r"^\d{8}$")
CONTRASENA_PATTERN = re.compile(r"^\d{4}$")


class RegistroIn(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    contrasena: str
  

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor: str) -> str:
        if not DNI_PATTERN.match(valor):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str) -> str:
        if not CONTRASENA_PATTERN.match(valor):
            raise ValueError("La contraseña debe tener exactamente 4 dígitos numéricos")
        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_texto_no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("No puede estar vacío")
        return valor.strip()


class LoginIn(BaseModel):
    dni: str
    contrasena: str

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor: str) -> str:
        if not DNI_PATTERN.match(valor):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos")
        return valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str) -> str:
        if not CONTRASENA_PATTERN.match(valor):
            raise ValueError("La contraseña debe tener exactamente 4 dígitos numéricos")
        return valor


class AuthOut(BaseModel):
    token: str
    dni: str
    role: str = "estudiante"
