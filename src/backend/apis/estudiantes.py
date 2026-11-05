from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response

from backend.apis.deps import requiere_auth
from backend.schemas.auth import RegistroIn
from backend.schemas.estudiantes import EstudianteOut, EstudianteUpdateIn
from backend.services import auth as auth_service
from backend.services import estudiantes as estudiantes_service

router = APIRouter(dependencies=[Depends(requiere_auth)])


@router.get("", response_model=list[EstudianteOut], status_code=200)
def listar(estado: Literal["AC", "IN"] | None = None) -> list[EstudianteOut]:
    return estudiantes_service.obtener_todos(estado)


@router.get("/{id_estudiante}", response_model=EstudianteOut, status_code=200)
def obtener(id_estudiante: int) -> EstudianteOut:
    try:
        return estudiantes_service.obtener(id_estudiante)
    except estudiantes_service.NoEncontrado:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")


@router.post("", response_model=EstudianteOut, status_code=201)
def crear(payload: RegistroIn) -> EstudianteOut:
    try:
        return estudiantes_service.crear(payload)
    except auth_service.DniYaRegistrado:
        raise HTTPException(status_code=409, detail="El DNI ya está registrado")


@router.put("/{id_estudiante}", response_model=EstudianteOut, status_code=200)
def actualizar(id_estudiante: int, payload: EstudianteUpdateIn) -> EstudianteOut:
    try:
        return estudiantes_service.actualizar(id_estudiante, payload)
    except estudiantes_service.NoEncontrado:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")


@router.delete("/{id_estudiante}", status_code=204)
def eliminar(id_estudiante: int) -> Response:
    try:
        estudiantes_service.eliminar(id_estudiante)
    except estudiantes_service.NoEncontrado:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return Response(status_code=204)
