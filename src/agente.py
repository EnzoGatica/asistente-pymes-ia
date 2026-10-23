"""Agente de atención de la panadería: herramientas propias, memoria por sesión, aprobación humana y trazas.

Bloque 1: herramientas (riesgo bajo: consultar_precio, calcular_total_pedido, consultar_estado_pedido;
          riesgo alto: generar_reembolso, que exige aprobación humana).
Bloque 2: agente y ejecutor con return_intermediate_steps.
Bloque 3: memoria entre interacciones (un historial por session_id) y registro de trazas en JSONL.
"""
import json
import threading
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from consumir_openai import MODELO
from negocio import DESPACHO, PEDIDOS, PRECIOS

ARCHIVO_TRAZAS = Path(__file__).resolve().parent.parent / "trazas_agente.jsonl"
REEMBOLSO_MAXIMO = 50000


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()


def buscar_producto(producto: str):
    for nombre, (precio, unidad) in PRECIOS.items():
        if normalizar(producto) in normalizar(nombre) or normalizar(nombre) in normalizar(producto):
            return nombre, precio, unidad
    return None


# --- Bloque 1: herramientas ---

@tool
def consultar_precio(producto: str) -> str:
    """Devuelve el precio de un producto de la panadería (marraqueta, hallulla, pan amasado, empanada
    de pino, torta 15 personas, torta 30 personas). Usar cuando el cliente pregunta cuánto vale algo."""
    encontrado = buscar_producto(producto)
    if encontrado is None:
        return f"No tenemos '{producto}' en la lista de precios."
    nombre, precio, unidad = encontrado
    return f"{nombre}: ${precio} por {unidad}"


@tool
def calcular_total_pedido(producto: str, cantidad: int, comuna: str = "") -> str:
    """Calcula el total de un pedido (precio x cantidad + despacho). Usar cuando el cliente quiere saber
    cuánto le sale un encargo. 'comuna' es opcional: vacía si retira en el local."""
    encontrado = buscar_producto(producto)
    if encontrado is None:
        return f"No tenemos '{producto}' en la lista de precios."
    if cantidad <= 0:
        return "La cantidad debe ser mayor que cero."
    nombre, precio, unidad = encontrado
    despacho = 0
    if comuna:
        if normalizar(comuna) not in DESPACHO:
            return f"No despachamos a {comuna}; solo a Tomé y Dichato (o retiro en el local)."
        despacho = DESPACHO[normalizar(comuna)]
    total = precio * cantidad + despacho
    return f"Total: ${total} ({cantidad} {unidad}(s) de {nombre} x ${precio} + despacho ${despacho})."


class ArgumentosEstadoPedido(BaseModel):
    numero_pedido: str = Field(description="Número del pedido, con formato P-1234.")
    incluir_historial: bool = Field(default=False, description="Si es True, incluye el historial completo del pedido.")


@tool("consultar_estado_pedido", args_schema=ArgumentosEstadoPedido)
def consultar_estado_pedido(numero_pedido: str, incluir_historial: bool = False) -> str:
    """Consulta el estado de un pedido ya hecho, con la opción de incluir su historial. Usar cuando el
    cliente pregunta por su pedido o encargo."""
    pedido = PEDIDOS.get(numero_pedido.strip().upper())
    if pedido is None:
        return f"No se encontró un pedido con el número {numero_pedido}."
    if not incluir_historial:
        return f"Pedido {numero_pedido}: {pedido['estado']}."
    return f"Pedido {numero_pedido}: {pedido['estado']} (historial: {'; '.join(pedido['historial'])})."


def preguntar_por_consola(mensaje: str, segundos: int = 60) -> bool:
    respuesta = []
    hilo = threading.Thread(target=lambda: respuesta.append(input(f"{mensaje} ¿Aprobar? (s/n): ")), daemon=True)
    hilo.start()
    hilo.join(segundos)
    return bool(respuesta) and respuesta[0].strip().lower() == "s"


aprobador = preguntar_por_consola  # se reemplaza en las pruebas, o por una notificación al dueño en producción


def esperar_aprobacion(mensaje: str) -> bool:
    """Bloquea la acción hasta que un humano la apruebe; sin respuesta a tiempo cuenta como rechazo."""
    return aprobador(mensaje)


@tool
def generar_reembolso(numero_pedido: str, monto: int) -> str:
    """Genera un reembolso de dinero para un pedido con problemas. Usar solo cuando el cliente pide
    explícitamente la devolución de su dinero. Siempre requiere aprobación del dueño."""
    pedido = PEDIDOS.get(numero_pedido.strip().upper())
    if pedido is None:
        return f"No se encontró un pedido con el número {numero_pedido}."
    tope = min(pedido["total"], REEMBOLSO_MAXIMO)
    if monto <= 0 or monto > tope:
        return f"Monto inválido: debe ser mayor que 0 y no superar ${tope}."
    aprobado = esperar_aprobacion(f"Reembolso de ${monto} para el pedido {numero_pedido}.")
    if not aprobado:
        return "El reembolso no fue aprobado por el dueño; el equipo contactará al cliente."
    return f"Reembolso de ${monto} aprobado y generado para el pedido {numero_pedido}."


HERRAMIENTAS = [consultar_precio, calcular_total_pedido, consultar_estado_pedido, generar_reembolso]


# --- Bloque 2: agente y ejecutor ---

def construir_ejecutor(modelo, herramientas=HERRAMIENTAS):
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

    prompt_agente = ChatPromptTemplate.from_messages([
        ("system", "Eres el asistente de atención de la Panadería La Espiga (Egaña 1450, Tomé). Usa las "
                   "herramientas cuando necesites precios, totales, estado de pedidos o reembolsos; no inventes "
                   "datos. Responde en español de Chile, en máximo 3 frases."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
    return AgentExecutor(agent=agente, tools=herramientas, return_intermediate_steps=True, max_iterations=5)


# --- Bloque 3: memoria y trazas ---

historiales = {}


def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def construir_agente_con_memoria(ejecutor):
    return RunnableWithMessageHistory(ejecutor, obtener_historial, input_messages_key="entrada",
                                      history_messages_key="chat_history", output_messages_key="output")


def registrar_traza(session_id, entrada, resultado, archivo=ARCHIVO_TRAZAS):
    traza = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {"herramienta": accion.tool, "argumentos": accion.tool_input, "observacion": str(observacion)}
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado["output"],
    }
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(traza, ensure_ascii=False) + "\n")
    return traza


def atender(agente_con_memoria, session_id, entrada):
    resultado = agente_con_memoria.invoke({"entrada": entrada}, {"configurable": {"session_id": session_id}})
    registrar_traza(session_id, entrada, resultado)
    return resultado


if __name__ == "__main__":
    load_dotenv()
    from langchain_openai import ChatOpenAI

    agente = construir_agente_con_memoria(construir_ejecutor(ChatOpenAI(model=MODELO, temperature=0)))
    conversaciones = [
        ("cliente_1", "¿Cuánto vale el kilo de hallulla?"),
        ("cliente_1", "Ok, ¿y cuánto me saldrían 3 kilos con despacho a Dichato?"),
        ("cliente_2", "¿Cómo va mi pedido P-1002? Quiero el historial completo."),
        ("cliente_2", "¿Y ese pedido a qué hora se entregó?"),
        ("cliente_3", "¿De qué pedido te pregunté recién?"),
        ("cliente_4", "¿Dónde queda el local?"),
        ("cliente_5", "La torta del pedido P-1002 llegó aplastada, quiero que me devuelvan $10000."),
        ("cliente_5", "Sí, confirmo: pedido P-1002, reembolso de $10000."),
    ]
    for session_id, entrada in conversaciones:
        resultado = atender(agente, session_id, entrada)
        herramientas = [accion.tool for accion, _ in resultado["intermediate_steps"]] or ["(ninguna)"]
        print(f"[{session_id}] {entrada}\n  herramientas: {', '.join(herramientas)}\n  respuesta: {resultado['output']}\n")
