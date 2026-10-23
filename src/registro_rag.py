"""Instrumenta el flujo RAG completo: tiempo por etapa, tokens reales y costo, en registros_latencia_costo.jsonl."""
import json
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from consumir_openai import MODELO, PRECIOS
from recuperacion import PROMPT_TEMPLATE, formatear_contexto, recuperar

ARCHIVO_REGISTROS = Path(__file__).resolve().parent.parent / "registros_latencia_costo.jsonl"


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def costo_usd(tokens, modelo=MODELO):
    if not tokens:
        return None
    precio = PRECIOS[modelo]
    return round((tokens["input_tokens"] * precio["entrada"] + tokens["output_tokens"] * precio["salida"]) / 1_000_000, 8)


def registrar_consulta(pregunta, chat_model, k=3):
    """Corre una consulta RAG real midiendo cada etapa y los tokens reales de la respuesta."""
    tiempos = {}
    with medir(tiempos, "embed_y_busqueda"):
        chunks = recuperar(pregunta, k)
    contexto, _ = formatear_contexto(chunks)
    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta))
    tokens = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
    if tokens:
        tokens = {clave: tokens[clave] for clave in ("input_tokens", "output_tokens", "total_tokens")}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "modelo": MODELO,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": tokens,
        "costo_generacion_usd": costo_usd(tokens),
    }


def guardar(registro, archivo=ARCHIVO_REGISTROS):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    load_dotenv()
    from langchain_openai import ChatOpenAI

    chat_model = ChatOpenAI(model=MODELO, temperature=0)
    recuperar("calentamiento", 1)  # abre el vector store antes de medir, para no sumar la carga inicial
    consultas = [(p, 3) for p in sys.argv[1:]] or [
        ("¿Despachan a Penco?", 3),
        ("¿Cuánto cuesta una torta selva negra para 30 personas?", 3),
        ("Me llegó el pan en mal estado, ¿qué hago?", 3),
        ("¿Cuánto cuesta una torta selva negra para 30 personas?", 6),
    ]
    for pregunta, k in consultas:
        registro = registrar_consulta(pregunta, chat_model, k)
        guardar(registro)
        print(f"k={k} embed_y_busqueda={registro['tiempos_ms']['embed_y_busqueda']} ms "
              f"generacion={registro['tiempos_ms']['generacion']} ms input_tokens={registro['tokens']['input_tokens']} "
              f"costo=USD {registro['costo_generacion_usd']:.8f}  {pregunta}")
