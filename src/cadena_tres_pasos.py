"""Chain de tres pasos: clasificar el mensaje del cliente -> redactar respuesta -> revisar el tono.

Paso 1 (clasificar): decide de qué trata el mensaje (pedido, precio, horario, reclamo u otro).
Paso 2 (redactar): escribe un borrador usando la ficha del negocio y la categoría del paso 1.
Paso 3 (revisar): corrige el tono del borrador para que suene cercano y profesional, sin cambiar datos.
"""
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from consumir_openai import MODELO
from negocio import FICHA_NEGOCIO


def construir_cadena(modelo):
    paso_clasificar = (
        PromptTemplate.from_template(
            "Clasifica este mensaje de un cliente de panadería en una sola palabra: pedido, precio, "
            "horario, reclamo u otro. Responde solo con la palabra.\n\nMensaje: {mensaje}"
        )
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )
    paso_redactar = (
        PromptTemplate.from_template(
            "Eres el asistente de esta panadería:\n{ficha}\n\n"
            "El mensaje del cliente fue clasificado como '{categoria}'. Redacta un borrador de respuesta "
            "de máximo 3 frases, usando solo datos de la ficha.\n\nMensaje: {mensaje}"
        )
        | modelo
        | StrOutputParser()
    )
    paso_revisar = (
        PromptTemplate.from_template(
            "Revisa el tono de este borrador para WhatsApp: cercano, amable y profesional, en español de "
            "Chile, sin emojis de más. No cambies precios, horarios ni datos. Devuelve solo el texto final."
            "\n\nBorrador: {borrador}"
        )
        | modelo
        | StrOutputParser()
    )
    return (
        RunnablePassthrough.assign(categoria=paso_clasificar, ficha=lambda _: FICHA_NEGOCIO)
        | paso_redactar
        | (lambda borrador: {"borrador": borrador})
        | paso_revisar
    )


if __name__ == "__main__":
    load_dotenv()
    from langchain_openai import ChatOpenAI

    cadena = construir_cadena(ChatOpenAI(model=MODELO))
    mensaje = "Hola!! necesito una torta para 30 personas pal sábado, ¿me la pueden llevar a Dichato? cuánto sería todo"
    print("Mensaje:", mensaje)
    print("Respuesta final:", cadena.invoke({"mensaje": mensaje}))
