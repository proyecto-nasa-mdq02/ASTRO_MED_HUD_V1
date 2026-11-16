import pytest
from fastapi.testclient import TestClient
from src.infraestructura.api.servidor import app
from src.infraestructura.api.inyector_dependencias import obtener_uow
from src.dominio.entidades import Tripulante


@pytest.fixture
def cliente_http(uow_memoria, adaptador_hash):
    """Sobrescribe la dependencia de base de datos para testear la API en memoria RAM."""
    with uow_memoria:
        uow_memoria.tripulantes.guardar(
            Tripulante(
                usuario="admin",
                password_hash=adaptador_hash.generar_hash("admin123"),
                nombres="Elena",
                apellidos="Vega",
                codigo_astronauta="AST-001",
                rol="Comandante Medico",
                especialidad="Medicina Aeroespacial",
            )
        )
        uow_memoria.tripulantes.guardar(
            Tripulante(
                usuario="astronauta_1",
                password_hash=adaptador_hash.generar_hash("123"),
                nombres="Neil",
                apellidos="Armstrong",
                codigo_astronauta="AST-002",
                rol="Especialista de Mision",
                especialidad="Piloto EVA",
            )
        )

    app.dependency_overrides[obtener_uow] = lambda: uow_memoria
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_api_login_exitoso_y_credenciales_invalidas(cliente_http):
    resp_ok = cliente_http.post("/api/login", json={"usuario": "admin", "password": "admin123"})
    assert resp_ok.status_code == 200
    assert resp_ok.json()["rol"] == "Comandante Medico"
    assert "password_hash" not in resp_ok.json()

    resp_fail = cliente_http.post("/api/login", json={"usuario": "admin", "password": "erronea"})
    assert resp_fail.status_code == 401


def test_api_bloqueo_rbac_especialista_intentando_crear_tripulante(cliente_http):
    # X-Operador-Id: 2 corresponde a 'astronauta_1' (Especialista de Mision).
    resp = cliente_http.post(
        "/api/tripulantes",
        headers={"X-Operador-Id": "2"},
        json={
            "usuario": "intruso",
            "nombres": "Buzz",
            "apellidos": "Aldrin",
            "codigo_astronauta": "AST-003",
            "rol": "Comandante Medico",
        },
    )
    assert resp.status_code == 403
    assert "Acceso denegado" in resp.json()["detalle"]


def test_api_registro_telemetria_y_simulador_crisis_solar(cliente_http):
    resp_sim = cliente_http.post(
        "/api/telemetria/simular-crisis",
        json={"id_tripulante": 2, "escenario": "TORMENTA_SOLAR"},
    )
    assert resp_sim.status_code == 201
    datos = resp_sim.json()
    assert datos["diagnostico"]["nivel_alerta_global"] == "CRITICO"
    assert datos["diagnostico"]["estado_sistemas"]["CARDIO_RAD"] == "CRITICO"
    assert datos["racha_actualizada"] == 1

    # Verificar que la analítica Pandas devuelve la serie temporal.
    resp_bi = cliente_http.get("/api/analitica/2")
    assert resp_bi.status_code == 200
    assert resp_bi.json()["total_lecturas"] == 1
    assert resp_bi.json()["distribucion_alertas"]["CRITICO"] == 1


def test_api_consola_sql_bloquea_borrado_y_permite_select(cliente_http):
    resp_select = cliente_http.post(
        "/api/consola-sql",
        json={"query": "SELECT usuario, rol FROM vista_tripulacion_activa"},
    )
    assert resp_select.status_code == 200
    assert len(resp_select.json()["filas"]) == 2

    resp_drop = cliente_http.post(
        "/api/consola-sql",
        json={"query": "DELETE FROM tripulantes WHERE id = 1"},
    )
    assert resp_drop.status_code == 403


def test_api_sincronizacion_idioma_y_cambio_mision_interplanetaria(cliente_http):
    # 1. Verifica cambio de idioma a Inglés (EN) y lectura desde el HUD
    resp_id = cliente_http.post("/api/idioma", json={"idioma": "en"})
    assert resp_id.status_code == 200
    assert resp_id.json()["idioma"] == "en"

    resp_get_id = cliente_http.get("/api/idioma")
    assert resp_get_id.status_code == 200
    assert resp_get_id.json()["idioma"] == "en"

    # Restaura idioma a Español (ES)
    cliente_http.post("/api/idioma", json={"idioma": "es"})

    # 2. Verifica conmutación en vivo a Misión Ares (Marte) con 7 tripulantes (105 lecturas)
    resp_mision = cliente_http.post(
        "/api/telemetria/cargar-mision",
        json={"mision": "ARES_MARTE"},
    )
    assert resp_mision.status_code == 200

    resp_trip = cliente_http.get("/api/tripulantes")
    assert resp_trip.status_code == 200
    assert len(resp_trip.json()) == 7