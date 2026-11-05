from datetime import date
from typing import Any

from backend.db import transaction

ID_DOCENTE_DEFAULT = 0
ESTADO_ACTIVO = "AC"
ESTADO_INACTIVO = "IN"
CANTIDAD_COPAS_INICIAL = 0

COLUMNAS_CRUD = (
    "id_estudiante",
    "dni",
    "nombres",
    "apellidos",
    "fecha_nacimiento",
    "id_grado",
    "estado",
    "cantidad_copas",
)

CAMPOS_ACTUALIZABLES = (
    "nombres",
    "apellidos",
    "fecha_nacimiento",
    "contrasena",
    "id_grado",
    "estado",
)


def find_by_dni(dni: str) -> dict[str, Any] | None:
    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_estudiante, dni, contrasena, estado "
                "FROM estudiante WHERE dni = %s",
                (dni,),
            )
            return cur.fetchone()


def insert(
    *,
    dni: str,
    nombres: str,
    apellidos: str,
    fecha_nacimiento: date | None,
    contrasena: str,
    
) -> int:
    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO estudiante "
                "(dni, nombres, apellidos, fecha_nacimiento, contrasena, "
                "cantidad_copas, estado) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    dni,
                    nombres,
                    apellidos,
                    fecha_nacimiento,
                    contrasena,
                    CANTIDAD_COPAS_INICIAL,
                    ESTADO_ACTIVO,
                  
                   
                ),
            )
            return cur.lastrowid


def find_all(estado: str | None = None) -> list[dict[str, Any]]:
    sql = (
        "SELECT "
        + ", ".join(COLUMNAS_CRUD)
        + " FROM estudiante"
    )
    params: tuple[Any, ...] = ()
    if estado is not None:
        sql += " WHERE estado = %s"
        params = (estado,)
    sql += " ORDER BY apellidos, nombres"

    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def find_by_id(id_estudiante: int) -> dict[str, Any] | None:
    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT "
                + ", ".join(COLUMNAS_CRUD)
                + " FROM estudiante WHERE id_estudiante = %s",
                (id_estudiante,),
            )
            return cur.fetchone()


def update(id_estudiante: int, campos: dict[str, Any]) -> None:
    claves = [c for c in CAMPOS_ACTUALIZABLES if c in campos and campos[c] is not None]
    if not claves:
        return

    sets = ", ".join(f"{c} = %s" for c in claves)
    valores = tuple(campos[c] for c in claves)

    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE estudiante SET {sets} WHERE id_estudiante = %s",
                (*valores, id_estudiante),
            )


def set_estado(id_estudiante: int, estado: str) -> int:
    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE estudiante SET estado = %s WHERE id_estudiante = %s",
                (estado, id_estudiante),
            )
            return cur.rowcount
