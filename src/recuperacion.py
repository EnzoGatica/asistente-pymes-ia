"""Recuperación semántica sobre vectorstore/ y prompt dinámico que obliga a citar fuentes."""
from functools import lru_cache

from dotenv import load_dotenv

from consumir_openai import MODELO
from indexar_corpus import PERSIST_DIRECTORY, crear_embeddings

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


@lru_cache(maxsize=None)
def abrir_vectorstore(persist_directory=PERSIST_DIRECTORY):
    from langchain_chroma import Chroma

    return Chroma(persist_directory=persist_directory, embedding_function=crear_embeddings())


def formatear_contexto(chunks_recuperados):
    """Arma el contexto numerado para el prompt y el mapa numero -> fuente para reconstruir la cita."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = doc.metadata.get("fuente", "desconocida")
    return "\n\n".join(lineas), citas


def recuperar(pregunta, k=3, persist_directory=PERSIST_DIRECTORY):
    return abrir_vectorstore(persist_directory).as_retriever(search_kwargs={"k": k}).invoke(pregunta)


def construir_prompt(pregunta, persist_directory=PERSIST_DIRECTORY, k=3):
    contexto, citas = formatear_contexto(recuperar(pregunta, k, persist_directory))
    return PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta), citas


def responder(pregunta, modelo, k=3):
    prompt, citas = construir_prompt(pregunta, k=k)
    return modelo.invoke(prompt).content, citas


if __name__ == "__main__":
    load_dotenv()
    from langchain_openai import ChatOpenAI

    modelo = ChatOpenAI(model=MODELO, temperature=0)
    for pregunta in [
        "¿Hasta qué hora puedo pedir para que el despacho salga a las 17:00?",
        "¿La hallulla tiene grasa animal?",
        "¿Tienen estacionamiento para clientes?",
    ]:
        prompt, citas = construir_prompt(pregunta)
        respuesta, _ = responder(pregunta, modelo)
        print(f"Pregunta: {pregunta}\nCitas: {citas}\nRespuesta: {respuesta}\n")
    print("--- Prompt completo de la primera pregunta ---")
    print(construir_prompt("¿Hasta qué hora puedo pedir para que el despacho salga a las 17:00?")[0])
