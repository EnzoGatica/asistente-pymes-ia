"""Componente: asegurar_cita (respuesta del modelo + fuentes usadas -> respuesta que cita)."""
from servicio_rag import asegurar_cita

FUENTES = ["despacho.md", "horarios.md"]


def test_si_el_modelo_ya_cito_una_fuente_usada_no_se_toca():
    texto = "Despachamos a Dichato por $3.500 [despacho.md]."
    assert asegurar_cita(texto, FUENTES) == texto


def test_si_el_modelo_no_cito_se_agregan_las_fuentes_al_final():
    assert asegurar_cita("Despachamos a Dichato.", FUENTES) == (
        "Despachamos a Dichato. [Fuentes: despacho.md, horarios.md]"
    )


def test_una_cita_a_un_documento_no_usado_no_cuenta():
    resultado = asegurar_cita("Ver [inventado.md].", FUENTES)
    assert resultado.endswith("[Fuentes: despacho.md, horarios.md]")


def test_contrato_la_salida_siempre_menciona_alguna_fuente_usada():
    for texto in ("Sin cita.", "Con cita [horarios.md].", "Cita falsa [x.md]."):
        resultado = asegurar_cita(texto, FUENTES)
        assert isinstance(resultado, str)
        assert any(f in resultado for f in FUENTES)
