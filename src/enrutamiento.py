"""Chain con enrutamiento condicional y manejo de errores por paso.

1) Clasificación: pedido, reclamo o consulta (ruta por defecto).
2) Rutas: cada categoría tiene su propio prompt.
3) Bifurcación con RunnableBranch, fallback en la ruta de reclamos y try/except general.
"""
import logging

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

from consumir_openai import MODELO
from negocio import FICHA_NEGOCIO

logger = logging.getLogger("enrutamiento")

respuesta_generica = RunnableLambda(
    lambda _: "Lamentamos lo ocurrido. Tu reclamo quedó registrado y nuestro equipo te contactará hoy "
              "por WhatsApp para solucionarlo."
)


def normalizar_categoria(texto: str) -> str:
    return texto.strip().strip(".").lower()


def construir_paso_clasificacion(modelo):
    return (
        PromptTemplate.from_template(
            "Clasifica el mensaje de un cliente de panadería en una sola palabra: pedido (quiere encargar "
            "o comprar), reclamo (algo salió mal) o consulta (pregunta de horario, precio, despacho u otra). "
            "Responde solo con esa palabra.\n\nMensaje: {mensaje}"
        )
        | modelo
        | StrOutputParser()
        | normalizar_categoria
    )


def construir_rutas(modelo):
    def ruta(instruccion):
        return (
            PromptTemplate.from_template(
                "Eres el asistente de esta panadería:\n{ficha}\n\n" + instruccion + "\n\nMensaje: {mensaje}"
            )
            | modelo
            | StrOutputParser()
        )

    return {
        "pedido": ruta("El cliente quiere hacer un pedido. Confirma producto, cantidad, precio total con "
                       "despacho si corresponde, y recuerda la anticipación necesaria. Máximo 3 frases."),
        "reclamo": ruta("El cliente tiene un reclamo. Reconoce el problema con empatía antes de ofrecer "
                        "una solución; no prometas reembolsos, di que el equipo lo contactará. Máximo 3 frases."),
        "consulta": ruta("Responde la consulta del cliente con los datos de la ficha. Si el dato no está, "
                         "dilo. Máximo 2 frases."),
    }


def construir_cadena_queja_segura(cadena_queja):
    return cadena_queja.with_fallbacks([respuesta_generica])


def construir_cadena_con_enrutamiento(modelo=None, paso_clasificacion=None, rutas=None):
    paso_clasificacion = paso_clasificacion or construir_paso_clasificacion(modelo)
    rutas = rutas or construir_rutas(modelo)
    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "pedido", rutas["pedido"]),
        (lambda x: x["categoria"] == "reclamo", construir_cadena_queja_segura(rutas["reclamo"])),
        rutas["consulta"],
    )
    return RunnablePassthrough.assign(categoria=paso_clasificacion, ficha=lambda _: FICHA_NEGOCIO) | bifurcacion


def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:  # último resguardo: ningún fallo deja al cliente sin respuesta
        logger.error("Error procesando mensaje %r: %s", mensaje, error)
        print(f"Error procesando mensaje: {error}")
        return "No pudimos procesar tu mensaje en este momento. Intenta de nuevo más tarde."


if __name__ == "__main__":
    load_dotenv()
    from langchain_openai import ChatOpenAI

    modelo = ChatOpenAI(model=MODELO)
    cadena = construir_cadena_con_enrutamiento(modelo)
    for mensaje in [
        "Quiero encargar 2 kilos de hallulla para mañana con despacho en Tomé",
        "Compré empanadas ayer y venían frías y con poco pino, muy mala onda",
        "¿Atienden el domingo en la tarde?",
    ]:
        categoria = construir_paso_clasificacion(modelo).invoke({"mensaje": mensaje})
        print(f"Mensaje: {mensaje}\nCategoría: {categoria}\nRespuesta: {procesar_mensaje_seguro(cadena, mensaje)}\n")
