"""Asistente de consultas para pymes: clasifica el mensaje de un cliente y propone una respuesta.

Uso:
    python main.py "¿Hasta qué hora atienden hoy?"
    python main.py            (pide el mensaje por consola)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "prompts"))

from banco import BANCO_DE_PROMPTS  # noqa: E402
from consumir_openai import (  # noqa: E402
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

PROMPTS = {prompt["nombre"]: prompt for prompt in BANCO_DE_PROMPTS}


def ejecutar_prompt(nombre, mensaje):
    prompt = PROMPTS[nombre]
    url, body = armar_peticion(mensaje, prompt["system_instruction"], prompt.get("response_schema"))
    datos = enviar_peticion(url, body)
    return parsear_respuesta_json(extraer_texto(datos)), calcular_costo(datos)


def atender(mensaje):
    clasificacion, costo_1 = ejecutar_prompt("clasificar_consulta", mensaje)
    propuesta, costo_2 = ejecutar_prompt("responder_cliente", mensaje)
    return {**clasificacion, **propuesta}, costo_1 + costo_2


if __name__ == "__main__":
    mensaje = " ".join(sys.argv[1:]) or input("Mensaje del cliente: ")
    try:
        resultado, costo = atender(mensaje)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
        sys.exit(1)
    print(f"Categoría: {resultado['categoria']} (urgencia {resultado['urgencia']}/3)")
    print(f"Respuesta del modelo: {resultado['respuesta']}")
    print(f"Requiere atención humana: {'sí' if resultado['requiere_humano'] else 'no'}")
    print(f"Costo total: USD {costo:.7f}")
    print("Proceso terminado sin errores.")
