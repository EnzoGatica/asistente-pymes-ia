import verificar_decisiones as v


def test_las_decisiones_se_leen_con_sus_campos():
    decisiones = v.leer_decisiones()
    assert decisiones["D-01"]["Estado"] == "vigente"
    assert decisiones["D-02"]["Estado"] == "reemplazada"
    assert "LIM-01" in decisiones["D-06"]["Costo"]


def test_una_decision_sin_costo_no_pasa():
    decisiones = {
        f"D-0{i}": {"Estado": "vigente", "Contexto": "x",
                    "Decisión": "x", "Alternativas descartadas": "x"}
        for i in range(1, 6)
    }
    ok, evidencia = v.decisiones_completas(decisiones)
    assert not ok
    assert "Costo" in evidencia


def test_las_limitaciones_se_leen_de_la_tabla():
    filas = v.leer_limitaciones()
    assert filas["LIM-02"]["riesgo"] == "R-02"
    assert "alucinaciones:H-03" in filas["LIM-02"]["origen"]


def test_toda_limitacion_declarada_esta_registrada():
    ok, evidencia = v.limitaciones_completas(v.leer_limitaciones())
    assert ok, evidencia


def test_una_limitacion_declarada_y_no_registrada_se_nombra():
    filas = v.leer_limitaciones()
    filas.pop("LIM-01")
    ok, evidencia = v.limitaciones_completas(filas)
    assert not ok
    assert "ataques:A-03" in evidencia


def test_contrato_un_id_dentro_de_otra_palabra_no_cuenta_como_decision():
    assert v.ID_D.findall("Pedidos PED-1001 y D-03.") == ["D-03"]


def test_el_riesgo_debe_listar_los_origenes_de_la_limitacion(monkeypatch):
    riesgo = dict(next(r for r in v.riesgos.RIESGOS if r["id"] == "R-02"), limites=[])
    otros = [r for r in v.riesgos.RIESGOS if r["id"] != "R-02"]
    monkeypatch.setattr(v.riesgos, "RIESGOS", otros + [riesgo])
    ok, evidencia = v.limitaciones_utiles(v.leer_limitaciones())
    assert not ok
    assert "H-03" in evidencia
