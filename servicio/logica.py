"""Puente entre la API y el flujo RAG del Módulo 2 (servicio_rag.py). La API no conoce LangChain."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import servicio_rag  # noqa: E402  (agrega src/ al path)
from negocio import PEDIDOS  # noqa: E402


class PedidoNoEncontrado(Exception):
    pass


class ServicioNoDisponible(Exception):
    pass


_motor = None  # (vectorstore, chat_model): se arma en la primera consulta, así /docs funciona sin clave


def _obtener_motor():
    global _motor
    if _motor is None:
        from dotenv import load_dotenv
        from langchain_openai import ChatOpenAI

        from consumir_openai import MODELO
        from indexar_corpus import crear_embeddings

        from servicio import config

        load_dotenv(RAIZ / ".env")
        config.clave_modelo()  # sin clave falla aquí, con un mensaje claro, y no a mitad de la indexación
        vectorstore, estado = servicio_rag.cargar_indice(crear_embeddings())
        servicio_rag.evento("indice_cargado", **estado)
        _motor = (vectorstore, ChatOpenAI(model=MODELO, temperature=0))
    return _motor


def responder(pregunta):
    try:
        vectorstore, chat_model = _obtener_motor()
    except Exception as error:  # sin clave o sin índice: el cliente recibe 503, no un traceback
        servicio_rag.evento("motor_no_disponible", 40, tipo=type(error).__name__)
        raise ServicioNoDisponible() from error
    resultado = servicio_rag.responder(pregunta, vectorstore, chat_model)
    if resultado["respuesta"] == servicio_rag.ERROR_SERVICIO:
        raise ServicioNoDisponible()
    return resultado["respuesta"], resultado["fuentes"], resultado["trace_id"]


def estado_pedido(codigo):
    if codigo not in PEDIDOS:
        raise PedidoNoEncontrado(codigo)
    return {"codigo": codigo, **PEDIDOS[codigo]}
