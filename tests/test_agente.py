import json

import pytest

import agente
from agente import (
    calcular_total_pedido,
    consultar_estado_pedido,
    consultar_precio,
    generar_reembolso,
    obtener_historial,
    registrar_traza,
)


@pytest.fixture(autouse=True)
def limpiar_estado(monkeypatch):
    agente.historiales.clear()
    yield


# Herramientas de riesgo bajo

def test_consultar_precio_ignora_tildes_y_mayusculas():
    assert consultar_precio.invoke({"producto": "HALLULLA"}) == "hallulla: $2400 por kilo"


def test_consultar_precio_producto_inexistente():
    assert "No tenemos" in consultar_precio.invoke({"producto": "pan sin gluten"})


def test_calcular_total_con_despacho_a_dichato():
    assert calcular_total_pedido.invoke({"producto": "hallulla", "cantidad": 3, "comuna": "Dichato"}).startswith("Total: $10700")


def test_calcular_total_sin_despacho():
    assert calcular_total_pedido.invoke({"producto": "empanada de pino", "cantidad": 4}).startswith("Total: $10000")


def test_calcular_total_rechaza_comuna_sin_despacho():
    assert "No despachamos a Penco" in calcular_total_pedido.invoke({"producto": "hallulla", "cantidad": 1, "comuna": "Penco"})


def test_consultar_estado_pedido_con_y_sin_historial():
    sin = consultar_estado_pedido.invoke({"numero_pedido": "P-1002"})
    con = consultar_estado_pedido.invoke({"numero_pedido": "P-1002", "incluir_historial": True})
    assert "historial" not in sin
    assert "entregado 21-10 16:10" in con


def test_consultar_estado_pedido_inexistente():
    assert "No se encontró" in consultar_estado_pedido.invoke({"numero_pedido": "P-9999"})


# Herramienta de riesgo alto: aprobación humana

def test_reembolso_rechazado_no_se_genera(monkeypatch):
    monkeypatch.setattr(agente, "aprobador", lambda mensaje: False)
    assert "no fue aprobado" in generar_reembolso.invoke({"numero_pedido": "P-1002", "monto": 10000})


def test_reembolso_aprobado_se_genera_y_pide_aprobacion_una_vez(monkeypatch):
    pedidos_de_aprobacion = []
    monkeypatch.setattr(agente, "aprobador", lambda mensaje: pedidos_de_aprobacion.append(mensaje) or True)
    assert "aprobado y generado" in generar_reembolso.invoke({"numero_pedido": "P-1002", "monto": 10000})
    assert pedidos_de_aprobacion == ["Reembolso de $10000 para el pedido P-1002."]


def test_reembolso_sobre_el_total_se_rechaza_sin_pedir_aprobacion(monkeypatch):
    monkeypatch.setattr(agente, "aprobador", lambda mensaje: pytest.fail("no debió pedir aprobación"))
    assert "Monto inválido" in generar_reembolso.invoke({"numero_pedido": "P-1001", "monto": 999999})


# Memoria y trazas

def test_sesiones_distintas_no_comparten_historial():
    obtener_historial("cliente_1").add_user_message("pregunto por P-1002")
    assert len(obtener_historial("cliente_1").messages) == 1
    assert obtener_historial("cliente_2").messages == []


def test_registrar_traza_escribe_una_linea_jsonl(tmp_path):
    class Accion:
        tool = "consultar_precio"
        tool_input = {"producto": "hallulla"}

    archivo = tmp_path / "trazas.jsonl"
    registrar_traza("cliente_1", "¿precio?", {"output": "$2400", "intermediate_steps": [(Accion(), "hallulla: $2400")]}, archivo)
    traza = json.loads(archivo.read_text(encoding="utf-8"))
    assert traza["acciones"][0]["herramienta"] == "consultar_precio"
    assert traza["respuesta_final"] == "$2400"
