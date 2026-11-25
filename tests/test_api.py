"""La tabla de casos de casos.py contra la API, sin llamar a OpenAI: índice con embeddings
deterministas sobre una copia de corpus/ y un modelo simulado, pero el código real de servicio_rag.py."""
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage

from casos import CASOS, ejecutar_caso
from servicio import logica
from servicio.main import app
from servicio_rag import cargar_indice

RAIZ = Path(__file__).resolve().parent.parent
cliente = TestClient(app, raise_server_exceptions=False)


class ModeloFalso:
    def invoke(self, prompt):
        if "wifi" in str(prompt).lower():
            return AIMessage(content="Lo siento, no tengo información sobre la clave del wifi.")
        return AIMessage(content="Sí, despachamos a Dichato por $3.500 [despacho.md].")


@pytest.fixture(autouse=True, scope="module")
def motor_simulado(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("api")
    shutil.copytree(RAIZ / "corpus", tmp / "corpus")
    vectorstore, _ = cargar_indice(DeterministicFakeEmbedding(size=256), str(tmp / "vectorstore"), tmp / "corpus")
    anterior, logica._motor = logica._motor, (vectorstore, ModeloFalso())
    yield
    logica._motor = anterior


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_caso(caso):
    ok, estado, cuerpo = ejecutar_caso(cliente, caso)
    assert ok, (
        f"{caso['id']}: esperado {caso['estado']} con "
        f"{caso['contiene']!r}, obtenido {estado}: {cuerpo[:80]}"
    )


def test_proveedor_caido_responde_503_sin_detalles():
    class ModeloCaido:
        def invoke(self, prompt):
            raise ConnectionError("api.openai.com no responde")

    vectorstore, modelo = logica._motor
    logica._motor = (vectorstore, ModeloCaido())
    try:
        r = cliente.post("/consultas", json={"pregunta": "¿Despachan a Dichato?"})
    finally:
        logica._motor = (vectorstore, modelo)
    assert r.status_code == 503
    assert r.json()["codigo"] == "servicio_no_disponible"
    assert "openai" not in r.text.lower()
