import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app
from backend.repositories import estudiantes as repo

client = TestClient(app)

REGISTRO_VALIDO = {
    "dni": "12345678",
    "nombres": "Ana",
    "apellidos": "Perez",
    "fecha_nacimiento": "2010-05-15",
    "contrasena": "1234",
    "id_grado": 3,
}

LOGIN_VALIDO = {"dni": "12345678", "contrasena": "1234"}


def _mock_repo(monkeypatch, *, estudiante_existente=None, id_insertado=1):
    monkeypatch.setattr(repo, "find_by_dni", lambda dni: estudiante_existente)
    monkeypatch.setattr(repo, "insert", lambda **kwargs: id_insertado)


class TestRegistro:
    def test_registro_exitoso_devuelve_201_y_jwt(self, monkeypatch):
        _mock_repo(monkeypatch, id_insertado=7)
        resp = client.post("/api/auth/registro", json=REGISTRO_VALIDO)

        assert resp.status_code == 201
        body = resp.json()
        assert body["dni"] == "12345678"
        assert body["role"] == "estudiante"

        payload = pyjwt.decode(
            body["token"], settings.jwt_secret_key, algorithms=["HS256"]
        )
        assert payload["sub"] == "7"
        assert payload["dni"] == "12345678"
        assert payload["role"] == "estudiante"

    def test_registro_dni_duplicado_devuelve_409(self, monkeypatch):
        _mock_repo(
            monkeypatch,
            estudiante_existente={
                "id_estudiante": 1,
                "dni": "12345678",
                "contrasena": "1234",
                "estado": "AC",
            },
        )
        resp = client.post("/api/auth/registro", json=REGISTRO_VALIDO)

        assert resp.status_code == 409
        assert resp.json()["detail"] == "El DNI ya está registrado"

    def test_registro_dni_invalido_devuelve_422(self, monkeypatch):
        _mock_repo(monkeypatch)
        payload = {**REGISTRO_VALIDO, "dni": "1234567"}
        resp = client.post("/api/auth/registro", json=payload)

        assert resp.status_code == 422

    def test_registro_contrasena_invalida_devuelve_422(self, monkeypatch):
        _mock_repo(monkeypatch)
        payload = {**REGISTRO_VALIDO, "contrasena": "12a4"}
        resp = client.post("/api/auth/registro", json=payload)

        assert resp.status_code == 422

    def test_registro_id_grado_invalido_devuelve_422(self, monkeypatch):
        _mock_repo(monkeypatch)
        payload = {**REGISTRO_VALIDO, "id_grado": 7}
        resp = client.post("/api/auth/registro", json=payload)

        assert resp.status_code == 422


class TestLogin:
    def test_login_exitoso_devuelve_200_y_jwt(self, monkeypatch):
        _mock_repo(
            monkeypatch,
            estudiante_existente={
                "id_estudiante": 5,
                "dni": "12345678",
                "contrasena": "1234",
                "estado": "AC",
            },
        )
        resp = client.post("/api/auth/login", json=LOGIN_VALIDO)

        assert resp.status_code == 200
        body = resp.json()
        assert body["dni"] == "12345678"
        assert body["role"] == "estudiante"

        payload = pyjwt.decode(
            body["token"], settings.jwt_secret_key, algorithms=["HS256"]
        )
        assert payload["sub"] == "5"

    def test_login_contrasena_incorrecta_devuelve_401(self, monkeypatch):
        _mock_repo(
            monkeypatch,
            estudiante_existente={
                "id_estudiante": 5,
                "dni": "12345678",
                "contrasena": "9999",
                "estado": "AC",
            },
        )
        resp = client.post("/api/auth/login", json=LOGIN_VALIDO)

        assert resp.status_code == 401
        assert resp.json()["detail"] == "DNI o contraseña incorrectos"

    def test_login_dni_inexistente_devuelve_401(self, monkeypatch):
        _mock_repo(monkeypatch, estudiante_existente=None)
        resp = client.post("/api/auth/login", json=LOGIN_VALIDO)

        assert resp.status_code == 401
        assert resp.json()["detail"] == "DNI o contraseña incorrectos"

    def test_login_estudiante_inactivo_devuelve_401(self, monkeypatch):
        _mock_repo(
            monkeypatch,
            estudiante_existente={
                "id_estudiante": 5,
                "dni": "12345678",
                "contrasena": "1234",
                "estado": "IN",
            },
        )
        resp = client.post("/api/auth/login", json=LOGIN_VALIDO)

        assert resp.status_code == 401

    def test_login_dni_invalido_devuelve_422(self, monkeypatch):
        _mock_repo(monkeypatch)
        resp = client.post("/api/auth/login", json={"dni": "abc", "contrasena": "1234"})

        assert resp.status_code == 422
