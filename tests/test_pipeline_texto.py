from pipeline_texto import limpiar_texto, procesar_texto, tokenizar


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    assert procesar_texto("El Cielo, es AZUL!") == ["el", "cielo", "es", "azul"]


def test_procesar_texto_quita_signos_de_apertura_del_espanol():
    assert procesar_texto("¿Despachan a Dichato? ¡Sí!") == ["despachan", "a", "dichato", "sí"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    assert procesar_texto("¡¡¡...!!!") == []


def test_limpiar_texto_colapsa_espacios():
    assert limpiar_texto("  hola,\n\n mundo  ") == "hola mundo"


def test_tokenizar_texto_vacio():
    assert tokenizar("") == []
