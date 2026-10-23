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


from pipeline_texto import calcular_metricas, calcular_precision_cobertura_f1, resumir_metricas  # noqa: E402


def test_metricas_identicas_dan_uno():
    assert calcular_metricas("Abrimos a las 8.", "abrimos a las 8") == {"precision": 1.0, "cobertura": 1.0, "f1": 1.0}


def test_metricas_cuentan_repeticiones():
    # "muy" aparece una vez en la referencia: solo una de las tres repeticiones cuenta como acierto.
    resultado = calcular_precision_cobertura_f1(["muy", "rico"], ["muy", "muy", "muy", "rico"])
    assert resultado["precision"] == 0.5
    assert resultado["cobertura"] == 1.0


def test_metricas_sin_coincidencias_dan_cero():
    assert calcular_metricas("pan amasado", "tortas")["f1"] == 0.0


def test_metricas_respuesta_vacia_no_divide_por_cero():
    assert calcular_metricas("pan amasado", "...") == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}


def test_resumir_metricas_promedia():
    resultados = [{"precision": 1, "cobertura": 0.5, "f1": 0.5}, {"precision": 0, "cobertura": 0.5, "f1": 0.7}]
    assert resumir_metricas(resultados) == {"precision_promedio": 0.5, "cobertura_promedio": 0.5, "f1_promedio": 0.6}


def test_resumir_metricas_lista_vacia():
    assert resumir_metricas([])["f1_promedio"] == 0
