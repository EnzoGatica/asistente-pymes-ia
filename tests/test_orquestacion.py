from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    normalizar_categoria,
    procesar_mensaje_seguro,
)


def rutas_falsas():
    return {
        "pedido": RunnableLambda(lambda x: "ruta pedido"),
        "reclamo": RunnableLambda(lambda x: "ruta reclamo"),
        "consulta": RunnableLambda(lambda x: "ruta consulta"),
    }


def cadena_con_categoria(categoria):
    return construir_cadena_con_enrutamiento(paso_clasificacion=RunnableLambda(lambda x: categoria), rutas=rutas_falsas())


# Clasificación

def test_normalizar_categoria_quita_espacios_mayusculas_y_punto():
    assert normalizar_categoria("  Reclamo.\n") == "reclamo"


def test_clasificacion_con_modelo_mockeado_se_normaliza():
    modelo_falso = MagicMock(side_effect=[AIMessage(content=" PEDIDO "), AIMessage(content="respuesta de pedido")])
    cadena = construir_cadena_con_enrutamiento(modelo_falso)
    assert cadena.invoke({"mensaje": "quiero 2 kilos"}) == "respuesta de pedido"


# Enrutamiento: una prueba por ruta, incluida la de defecto

def test_ruta_pedido():
    assert cadena_con_categoria("pedido").invoke({"mensaje": "x"}) == "ruta pedido"


def test_ruta_reclamo():
    assert cadena_con_categoria("reclamo").invoke({"mensaje": "x"}) == "ruta reclamo"


def test_ruta_consulta():
    assert cadena_con_categoria("consulta").invoke({"mensaje": "x"}) == "ruta consulta"


def test_categoria_desconocida_cae_en_ruta_por_defecto():
    assert cadena_con_categoria("felicitacion").invoke({"mensaje": "x"}) == "ruta consulta"


# Manejo de errores por paso

def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    def fallar_a_proposito(x):
        raise ConnectionError("simulado")

    cadena_queja_segura = construir_cadena_queja_segura(RunnableLambda(fallar_a_proposito))
    assert "equipo" in cadena_queja_segura.invoke({"mensaje": "esto no funciona"}).lower()


def test_flujo_completo_usa_fallback_si_falla_la_ruta_reclamo():
    rutas = rutas_falsas()
    rutas["reclamo"] = RunnableLambda(lambda x: (_ for _ in ()).throw(TimeoutError("simulado")))
    cadena = construir_cadena_con_enrutamiento(paso_clasificacion=RunnableLambda(lambda x: "reclamo"), rutas=rutas)
    assert "equipo" in procesar_mensaje_seguro(cadena, "venía crudo").lower()


def test_procesar_mensaje_seguro_no_propaga_excepciones():
    clasificacion_falsa = MagicMock(side_effect=ConnectionError("simulado"))
    cadena_falsa = construir_cadena_con_enrutamiento(paso_clasificacion=clasificacion_falsa, rutas=rutas_falsas())
    assert "no pudimos procesar" in procesar_mensaje_seguro(cadena_falsa, "mensaje de prueba").lower()
