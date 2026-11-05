from datetime import datetime, timedelta, timezone

import jwt as pyjwt
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app
from backend.repositories import estudiantes as repo

client = TestClient(app)

ESTUDIANTE_FILA = {
    "id_estudiante": 7,
    "dni": "12345678",
    "nombres": "Ana",
    "apellidos": "Perez",
    "fecha_nacimiento": "2010-05-15",
    "id_grado": 3,
    "estado": "AC",
    "cantidad_copas": 0,
}

ESTUDIANTE_BODY = {
    "dni": "12345678",
    "nombres": "Ana",
    "apellidos": "Perez",
    "fecha_nacimiento": "2010-05-15",
    "contrasena": "1234",
    "id_grado": 3,
}


def _token_valido() -> str:
    ahora = datetime.now(timezone.utc)
    return pyjwt.encode(
        {
            "sub": "1",
            "dni": "87654321",
            "role": "estudiante",
            "iat": ahora,
            "exp": ahora + timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def _token_expirado() -> str:
    ahora = datetime.now(timezone.utc)
    return pyjwt.encode(
        {
            "sub": "1",
            "dni": "87654321",
            "role": "estudiante",
            "iat": ahora - timedelta(hours=2),
            "exp": ahora - timedelta(hours=1),
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_token_valido()}"}


class TestAutenticacionRequerida:
    def test_sin_token_devuelve_401(self):
        resp = client.get("/api/estudiantes")
        assert resp.status_code == 401

    def test_token_basura_devuelve_401(self):
        resp = client.get(
            "/api/estudiantes", headers={"Authorization": "Bearer no-es-jwt"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Token inválido o expirado"

    def test_token_expirado_devuelve_401(self):
        resp = client.get(
            "/api/estudiantes",
            headers={"Authorization": f"Bearer {_token_expirado()}"},
        )
        assert resp.status_code == 401

    def test_secretario_invalido_devuelve_401(self):
        otro = pyjwt.encode(
            {"sub": "1", "role": "estudiante"},
            "otro-secreto-completamente-distinto",
            algorithm="HS256",
        )
        resp = client.get(
            "/api/estudiantes", headers={"Authorization": f"Bearer {otro}"}
        )
        assert resp.status_code == 401


class TestListar:
    def test_listar_devuelve_200_y_lista(self, monkeypatch):
        monkeypatch.setattr(repo, "find_all", lambda estado=None: [ESTUDIANTE_FILA])
        resp = client.get("/api/estudiantes", headers=_headers())

        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["dni"] == "12345678"
        assert "contrasena" not in body[0]

    def test_listar_filtra_por_estado(self, monkeypatch):
        capturado = {}

        def find_all(estado=None):
            capturado["estado"] = estado
            return []

        monkeypatch.setattr(repo, "find_all", find_all)
        resp = client.get(
            "/api/estudiantes", params={"estado": "IN"}, headers=_headers()
        )

        assert resp.status_code == 200
        assert resp.json() == []
        assert capturado["estado"] == "IN"


class TestObtener:
    def test_obtener_devuelve_200(self, monkeypatch):
        monkeypatch.setattr(repo, "find_by_id", lambda id_: ESTUDIANTE_FILA)
        resp = client.get("/api/estudiantes/7", headers=_headers())

        assert resp.status_code == 200
        assert resp.json()["id_estudiante"] == 7

    def test_obtener_inexistente_devuelve_404(self, monkeypatch):
        monkeypatch.setattr(repo, "find_by_id", lambda id_: None)
        resp = client.get("/api/estudiantes/99", headers=_headers())

        assert resp.status_code == 404


class TestCrear:
    def test_crear_devuelve_201(self, monkeypatch):
        monkeypatch.setattr(repo, "find_by_dni", lambda dni: None)
        monkeypatch.setattr(repo, "insert", lambda **kwargs: 7)
        monkeypatch.setattr(repo, "find_by_id", lambda id_: ESTUDIANTE_FILA)

        resp = client.post(
            "/api/estudiantes", json=ESTUDIANTE_BODY, headers=_headers()
        )

        assert resp.status_code == 201
        body = resp.json()
        assert body["dni"] == "12345678"
        assert body["estado"] == "AC"
        assert "contrasena" not in body

    def test_crear_dni_duplicado_devuelve_409(self, monkeypatch):
        monkeypatch.setattr(
            repo,
            "find_by_dni",
            lambda dni: {
                "id_estudiante": 1,
                "dni": dni,
                "contrasena": "1234",
                "estado": "AC",
            },
        )

        resp = client.post(
            "/api/estudiantes", json=ESTUDIANTE_BODY, headers=_headers()
        )

        assert resp.status_code == 409
        assert resp.json()["detail"] == "El DNI ya está registrado"

    def test_crear_dni_invalido_devuelve_422(self, monkeypatch):
        monkeypatch.setattr(repo, "find_by_dni", lambda dni: None)
        resp = client.post(
            "/api/estudiantes",
            json={**ESTUDIANTE_BODY, "dni": "1234567"},
            headers=_headers(),
        )

        assert resp.status_code == 422


class TestActualizar:
    def test_actualizar_devuelve_200_y_solo_envia_campos(self, monkeypatch):
        capturado = {}

        def update(id_estudiante, campos):
            capturado["id"] = id_estudiante
            capturado["campos"] = campos

        actualizado = {**ESTUDIANTE_FILA, "nombres": "Maria"}
        monkeypatch.setattr(repo, "update", update)
        monkeypatch.setattr(repo, "find_by_id", lambda id_: actualizado)

        resp = client.put(
            "/api/estudiantes/7",
            json={"nombres": "Maria", "apellidos": None},
            headers=_headers(),
        )

        assert resp.status_code == 200
        assert resp.json()["nombres"] == "Maria"
        assert capturado["id"] == 7
        assert capturado["campos"] == {"nombres": "Maria"}

    def test_actualizar_inexistente_devuelve_404(self, monkeypatch):
        monkeypatch.setattr(repo, "find_by_id", lambda id_: None)
        resp = client.put(
            "/api/estudiantes/99", json={"nombres": "X"}, headers=_headers()
        )

        assert resp.status_code == 404

    def test_actualizar_contrasena_invalida_devuelve_422(self, monkeypatch):
        resp = client.put(
            "/api/estudiantes/7",
            json={"contrasena": "12"},
            headers=_headers(),
        )

        assert resp.status_code == 422

    def test_actualizar_estado_invalido_devuelve_422(self, monkeypatch):
        resp = client.put(
            "/api/estudiantes/7",
            json={"estado": "XX"},
            headers=_headers(),
        )

        assert resp.status_code == 422

    def test_actualizar_puede_reactivar(self, monkeypatch):
        capturado = {}
        inactivo = {**ESTUDIANTE_FILA, "estado": "IN"}

        def update(id_estudiante, campos):
            capturado["campos"] = campos

        monkeypatch.setattr(repo, "update", update)
        monkeypatch.setattr(repo, "find_by_id", lambda id_: inactivo)

        resp = client.put(
            "/api/estudiantes/7", json={"estado": "AC"}, headers=_headers()
        )

        assert resp.status_code == 200
        assert capturado["campos"] == {"estado": "AC"}


class TestEliminar:
    def test_eliminar_devuelve_204_y_ponen_inactivo(self, monkeypatch):
        capturado = {}

        def set_estado(id_estudiante, estado):
            capturado["id"] = id_estudiante
            capturado["estado"] = estado
            return 1

        monkeypatch.setattr(repo, "set_estado", set_estado)

        resp = client.delete("/api/estudiantes/7", headers=_headers())

        assert resp.status_code == 204
        assert resp.content == b""
        assert capturado == {"id": 7, "estado": "IN"}

    def test_eliminar_inexistente_devuelve_404(self, monkeypatch):
        monkeypatch.setattr(repo, "set_estado", lambda id_estudiante, estado: 0)

        resp = client.delete("/api/estudiantes/99", headers=_headers())

        assert resp.status_code == 404
