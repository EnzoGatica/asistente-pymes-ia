"""Punto de supervisión humana: ninguna versión nueva del prompt entra a producción sin aprobación.

El grafo propone la huella nueva, se detiene con interrupt() y solo la activa si una persona reanuda
con Command(resume=True). Con Command(resume=False) se mantiene la versión anterior.
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    huella_activa: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
        "huella_actual": estado["huella_activa"],
    })
    return {"aprobado": decision is True}  # solo un True explícito aprueba; "no" o None no activan nada


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
        return {"huella_activa": estado["huella_nueva"]}
    print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior", estado["huella_activa"])
    return {}


def construir_grafo_despliegue():
    grafo = StateGraph(EstadoDespliegue)
    grafo.add_node("proponer", proponer)
    grafo.add_node("supervisar", supervisar)
    grafo.add_node("aplicar", aplicar)
    grafo.add_edge(START, "proponer")
    grafo.add_edge("proponer", "supervisar")
    grafo.add_edge("supervisar", "aplicar")
    grafo.add_edge("aplicar", END)
    return grafo.compile(checkpointer=InMemorySaver())


app_despliegue = construir_grafo_despliegue()

if __name__ == "__main__":
    from registro_prompts import registro

    v1, v2 = registro.versiones
    entrada = {"huella_nueva": v2["huella"], "huella_activa": v1["huella"], "aprobado": False}

    config = {"configurable": {"thread_id": "despliegue-prompt-1"}}
    resultado = app_despliegue.invoke(entrada, config=config)
    print("1) tras invocar, trae __interrupt__:", "__interrupt__" in resultado)
    print("2) pendiente:", app_despliegue.get_state(config).interrupts[0].value)
    resultado = app_despliegue.invoke(Command(resume=True), config=config)
    print("3) tras aprobar:", resultado)

    config2 = {"configurable": {"thread_id": "despliegue-prompt-2"}}
    app_despliegue.invoke(entrada, config=config2)
    resultado = app_despliegue.invoke(Command(resume=False), config=config2)
    print("4) tras rechazar:", resultado)

    config3 = {"configurable": {"thread_id": "despliegue-prompt-3"}}
    app_despliegue.invoke(entrada, config=config3)
    resultado = app_despliegue.invoke(Command(resume="no"), config=config3)
    print("5) reanudar con el texto 'no' tampoco activa:", resultado)
