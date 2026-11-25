"""Componente: formatear_contexto (fragmentos recuperados -> texto del contexto del prompt)."""
from langchain_core.documents import Document

from servicio_rag import formatear_contexto

DESPACHO = Document("Despachamos a Dichato ($3.500).", metadata={"fuente": "despacho.md"})
HORARIO = Document("Abrimos de lunes a sábado.", metadata={"fuente": "horarios.md"})


def test_cada_fragmento_lleva_su_fuente_entre_corchetes():
    assert formatear_contexto([DESPACHO]) == "[despacho.md] Despachamos a Dichato ($3.500)."


def test_varios_fragmentos_van_separados_por_linea_en_blanco():
    assert formatear_contexto([DESPACHO, HORARIO]).split("\n\n") == [
        "[despacho.md] Despachamos a Dichato ($3.500).",
        "[horarios.md] Abrimos de lunes a sábado.",
    ]


def test_sin_fragmentos_el_contexto_queda_vacio():
    assert formatear_contexto([]) == ""


def test_contrato_devuelve_texto_que_contiene_cada_fuente():
    contexto = formatear_contexto([DESPACHO, HORARIO])
    assert isinstance(contexto, str)
    assert all(f"[{d.metadata['fuente']}]" in contexto for d in (DESPACHO, HORARIO))
