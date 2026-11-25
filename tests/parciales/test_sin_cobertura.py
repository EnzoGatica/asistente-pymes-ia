"""Componente: DECLARA_SIN_INFO (texto del modelo -> ¿declara que el contexto no alcanza?)."""
from servicio_rag import DECLARA_SIN_INFO


def test_reconoce_no_contamos_con_informacion():
    assert DECLARA_SIN_INFO.search("Lo siento, no contamos con información sobre el wifi.")


def test_reconoce_no_tengo_informacion_sin_tilde_y_en_mayusculas():
    assert DECLARA_SIN_INFO.search("NO TENGO INFORMACION de eso.")


def test_una_respuesta_con_datos_no_se_marca():
    assert not DECLARA_SIN_INFO.search("Sí, despachamos a Dichato por $3.500 [despacho.md].")


def test_contrato_solo_marca_frases_de_falta_de_informacion():
    marcadas = [
        t for t in (
            "No dispongo de información sobre eso.",
            "No tenemos la información del sueldo.",
            "Tenemos información de despacho: $3.500.",
            "No despachamos a Penco.",
        ) if DECLARA_SIN_INFO.search(t)
    ]
    assert marcadas == ["No dispongo de información sobre eso.", "No tenemos la información del sueldo."]
