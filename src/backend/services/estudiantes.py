from backend.repositories import estudiantes as repo
from backend.schemas.auth import RegistroIn
from backend.schemas.estudiantes import EstudianteOut, EstudianteUpdateIn
from backend.services.auth import DniYaRegistrado


class NoEncontrado(Exception):
    pass


def _a_out(fila: dict) -> EstudianteOut:
    return EstudianteOut(**fila)


def obtener_todos(estado: str | None = None) -> list[EstudianteOut]:
    return [_a_out(f) for f in repo.find_all(estado)]


def obtener(id_estudiante: int) -> EstudianteOut:
    fila = repo.find_by_id(id_estudiante)
    if fila is None:
        raise NoEncontrado()
    return _a_out(fila)


def crear(datos: RegistroIn) -> EstudianteOut:
    if repo.find_by_dni(datos.dni) is not None:
        raise DniYaRegistrado()

    id_estudiante = repo.insert(
        dni=datos.dni,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        fecha_nacimiento=datos.fecha_nacimiento,
        contrasena=datos.contrasena,
       
    )
    return obtener(id_estudiante)


def actualizar(id_estudiante: int, datos: EstudianteUpdateIn) -> EstudianteOut:
    obtener(id_estudiante)

    campos = {
        clave: valor
        for clave, valor in datos.model_dump(exclude_unset=True).items()
        if valor is not None
    }
    if not campos:
        return obtener(id_estudiante)

    repo.update(id_estudiante, campos)
    return obtener(id_estudiante)


def eliminar(id_estudiante: int) -> None:
    if repo.set_estado(id_estudiante, repo.ESTADO_INACTIVO) == 0:
        raise NoEncontrado()
