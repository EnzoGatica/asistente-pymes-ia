from types import SimpleNamespace

from ejecutar_matriz import huella, motivos_de_falla


def respuesta(estado, texto, datos=None):
    def json():
        if datos is None:
            raise ValueError("no es JSON")
        return datos

    return SimpleNamespace(status_code=estado, text=texto, json=json)


def test_cumple_cuando_estado_y_contenido_coinciden():
    esperado = {"estado": 200, "contiene": ["30 dias"]}
    assert motivos_de_falla(esperado, respuesta(200, "30 dias")) == []


def test_avisa_del_estado_distinto():
    esperado = {"estado": 422, "contiene": ["pedido_id"]}
    r = respuesta(200, "pedido_id")
    assert motivos_de_falla(esperado, r) == [
        "estado 200, se esperaba 422"
    ]


def test_avisa_de_lo_que_falta_y_de_lo_que_sobra():
    esperado = {"estado": 200, "contiene": ["a"],
                "no_contiene": ["b"]}
    motivos = motivos_de_falla(esperado, respuesta(200, "b"))
    assert motivos == ["falta 'a'", "no debia aparecer 'b'"]


def test_compara_las_fuentes_cuando_se_piden():
    esperado = {"estado": 200, "fuentes": []}
    datos = {"fuentes": ["manual.pdf"]}
    r = respuesta(200, "", datos)
    assert motivos_de_falla(esperado, r) == [
        "fuentes ['manual.pdf'], se esperaba []"
    ]


def test_contrato_los_motivos_son_una_lista_de_textos():
    esperado = {"estado": 200, "contiene": ["x"], "fuentes": []}
    sin_fuentes = {"fuentes": []}
    for r in (respuesta(500, ""), respuesta(200, "x", sin_fuentes)):
        motivos = motivos_de_falla(esperado, r)
        assert isinstance(motivos, list)
        assert all(isinstance(m, str) for m in motivos)


def test_la_huella_cambia_si_cambia_un_escenario():
    uno = [{"id": "MP-01", "esperado": {"estado": 200}}]
    otro = [{"id": "MP-01", "esperado": {"estado": 201}}]
    assert huella(uno) == huella(list(uno))
    assert huella(uno) != huella(otro)
