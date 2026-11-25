"""Dobles de prueba para ejecutar ataques y sondas sin llamar a OpenAI.

El índice usa embeddings deterministas sobre una copia de corpus/ (más fragmentos extra si un ataque
los necesita) y el modelo responde un texto fijo. El resto del flujo es el código real de servicio_rag.py.
"""
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage

from servicio import logica
from servicio_rag import cargar_indice

RAIZ = Path(__file__).resolve().parent


class ModeloFijo:
    """Responde siempre lo mismo, venga o no del contexto."""

    def __init__(self, respuesta):
        self.respuesta = respuesta

    def invoke(self, prompt):
        return AIMessage(content=self.respuesta)


@contextmanager
def motor_simulado(respuesta, fragmentos_extra=None):
    """Reemplaza el motor de la API mientras dura el bloque. fragmentos_extra: {nombre.md: texto}."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        corpus = Path(tmp) / "corpus"
        if fragmentos_extra:
            # índice mínimo: así el fragmento del ataque siempre se recupera y lo que se mide es el filtro
            corpus.mkdir()
            shutil.copy(RAIZ / "corpus" / "despacho.md", corpus)
        else:
            shutil.copytree(RAIZ / "corpus", corpus)
        for nombre, texto in (fragmentos_extra or {}).items():
            (corpus / nombre).write_text(texto, encoding="utf-8")
        vectorstore, _ = cargar_indice(DeterministicFakeEmbedding(size=256), str(Path(tmp) / "vs"), corpus)
        anterior, logica._motor = logica._motor, (vectorstore, ModeloFijo(respuesta))
        try:
            yield
        finally:
            logica._motor = anterior
