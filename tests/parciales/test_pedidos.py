"""Componente: estado_pedido (código -> datos simulados del pedido, o PedidoNoEncontrado)."""
import pytest

from servicio.logica import PedidoNoEncontrado, estado_pedido


def test_pedido_entregado():
    assert estado_pedido("P-1002")["estado"] == "entregado"


def test_pedido_en_preparacion_trae_su_historial():
    pedido = estado_pedido("P-1001")
    assert pedido["estado"] == "en preparación"
    assert pedido["historial"][0].startswith("recibido")


def test_pedido_inexistente_lanza_pedido_no_encontrado():
    with pytest.raises(PedidoNoEncontrado):
        estado_pedido("P-9999")


def test_contrato_devuelve_las_claves_del_esquema_estado_pedido():
    for codigo in ("P-1001", "P-1002"):
        assert set(estado_pedido(codigo)) == {"codigo", "estado", "total", "historial"}
