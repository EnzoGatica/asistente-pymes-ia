"""Servicio RAG del Gate 2: indexa (incremental), recupera, filtra inyección, responde citando fuentes,
registra trazas y consumo, y exige supervisión humana para desplegar una versión nueva del prompt.

Uso:
    python servicio_rag.py "¿Despachan a Penco?"
    python servicio_rag.py            (corre dos consultas de ejemplo y el punto de supervisión)
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from dotenv import load_dotenv  # noqa: E402

from consumir_openai import MODELO  # noqa: E402
from indexar_corpus import PERSIST_DIRECTORY, cargar_corpus, crear_embeddings, partir_en_chunks  # noqa: E402
from logging_rag import evento, filtrar_documentos_sospechosos, huella, nueva_consulta, registrar_consumo  # noqa: E402
from registro_prompts import PROMPT_ACTUAL  # noqa: E402

SIN_CONTEXTO = "No tengo información suficiente y verificada para responder esto; te contactará alguien del equipo."
ERROR_SERVICIO = "No pudimos procesar tu mensaje en este momento. Intenta de nuevo en unos minutos."


def cargar_indice(embeddings, persist_directory=PERSIST_DIRECTORY, carpeta_corpus=None):
    """Abre el índice persistido y solo agrega, actualiza o borra los chunks que cambiaron en corpus/."""
    from langchain_chroma import Chroma

    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    chunks, ids = partir_en_chunks(*(cargar_corpus(carpeta_corpus) if carpeta_corpus else cargar_corpus()))
    guardados = vectorstore.get()
    texto_guardado = dict(zip(guardados["ids"], guardados["documents"]))
    nuevos = [(c, i) for c, i in zip(chunks, ids) if texto_guardado.get(i) != c.page_content]
    sobrantes = [i for i in texto_guardado if i not in set(ids)]
    a_borrar = sobrantes + [i for _, i in nuevos if i in texto_guardado]
    if a_borrar:
        vectorstore.delete(ids=a_borrar)
    if nuevos:
        vectorstore.add_documents([c for c, _ in nuevos], ids=[i for _, i in nuevos])
    estado = "indice_reutilizado" if not (nuevos or sobrantes) else ("indice_creado" if not texto_guardado else "indice_actualizado")
    return vectorstore, {"estado": estado, "chunks": len(ids), "agregados": len(nuevos), "borrados": len(sobrantes)}


def formatear_contexto(documentos):
    return "\n\n".join(f"[{d.metadata['fuente']}] {d.page_content}" for d in documentos)


def asegurar_cita(respuesta, fuentes):
    """Validación estructural: si el modelo no citó ninguna fuente usada, se agregan al final."""
    citadas = set(re.findall(r"\[([\w\-]+\.md)\]", respuesta))
    if citadas & set(fuentes):
        return respuesta
    return f"{respuesta} [Fuentes: {', '.join(fuentes)}]"


def responder(pregunta, vectorstore, chat_model, k=3):
    with nueva_consulta() as trace_id:
        auditoria = [evento("consulta_recibida", pregunta_len=len(pregunta or ""), pregunta_huella=huella(pregunta or ""))]
        try:
            if not pregunta or not pregunta.strip():
                raise ValueError("pregunta vacía")
            documentos = vectorstore.as_retriever(search_kwargs={"k": k}).invoke(pregunta)
            auditoria.append(evento("documentos_recuperados", n=len(documentos), fuentes=[d.metadata.get("fuente") for d in documentos]))
            limpios, descartados = filtrar_documentos_sospechosos(documentos)
            auditoria.append(evento("contexto_filtrado", n_limpios=len(limpios), n_descartados=len(descartados)))
            if not limpios:
                auditoria.append(evento("sin_contexto_confiable"))
                return {"trace_id": trace_id, "respuesta": SIN_CONTEXTO, "fuentes": [], "auditoria": auditoria}
            prompt = PROMPT_ACTUAL["texto"].format(contexto=formatear_contexto(limpios), pregunta=pregunta)
            mensaje = chat_model.invoke(prompt)
            auditoria.append(registrar_consumo(mensaje))
            fuentes = sorted({d.metadata["fuente"] for d in limpios})
            respuesta = asegurar_cita(mensaje.content, fuentes)
            auditoria.append(evento("respuesta_generada", respuesta_len=len(respuesta), prompt_huella=PROMPT_ACTUAL["huella"]))
            return {"trace_id": trace_id, "respuesta": respuesta, "fuentes": fuentes, "auditoria": auditoria}
        except Exception as error:  # el servicio nunca termina con un traceback frente al cliente
            auditoria.append(evento("error_servicio", 40, tipo=type(error).__name__))
            return {"trace_id": trace_id, "respuesta": ERROR_SERVICIO, "fuentes": [], "auditoria": auditoria}


def supervisar_despliegue(huella_nueva, huella_activa, decidir):
    """Pausa el despliegue con interrupt() y lo retoma con la decisión de una persona."""
    from langgraph.types import Command

    from grafo_supervision import app_despliegue

    config = {"configurable": {"thread_id": f"despliegue-{huella_nueva}-{huella(str(id(decidir)))}"}}
    pausado = app_despliegue.invoke({"huella_nueva": huella_nueva, "huella_activa": huella_activa, "aprobado": False}, config=config)
    pendiente = pausado["__interrupt__"][0].value
    return app_despliegue.invoke(Command(resume=decidir(pendiente)), config=config)


def preguntar_aprobacion(pendiente):
    print(f"Punto de supervisión: {pendiente['motivo']} (actual {pendiente['huella_actual']} -> propuesta {pendiente['huella_propuesta']})")
    try:
        return input("¿Aprobar? (s/n): ").strip().lower() == "s"
    except EOFError:
        print("Sin respuesta: se rechaza por defecto.")
        return False


def main():
    load_dotenv()
    from langchain_openai import ChatOpenAI

    from registro_prompts import registro

    vectorstore, estado_indice = cargar_indice(crear_embeddings())
    evento("indice_cargado", **estado_indice)
    chat_model = ChatOpenAI(model=MODELO, temperature=0)
    preguntas = sys.argv[1:] or [
        "¿Cuánto cuesta una torta selva negra para 30 personas y con cuánta anticipación la pido?",
        "¿Despachan a Penco? Mi correo es ana.perez@example.com",
    ]
    for pregunta in preguntas:
        resultado = responder(pregunta, vectorstore, chat_model)
        print(f"\nPregunta: {pregunta}\nRespuesta final: {resultado['respuesta']}\nFuentes: {', '.join(resultado['fuentes'])}\n")
    if len(sys.argv) == 1:
        anterior, actual = registro.versiones[-2:]
        final = supervisar_despliegue(actual["huella"], anterior["huella"], preguntar_aprobacion)
        print("Estado final del despliegue:", final)
    print("Proceso terminado sin errores.")


if __name__ == "__main__":
    main()
