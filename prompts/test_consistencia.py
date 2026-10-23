"""Ejecuta cada prompt del banco varias veces contra la API real y registra cuántas salidas son válidas."""
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from banco import BANCO_DE_PROMPTS  # noqa: E402
from consumir_openai import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json  # noqa: E402

INTENTOS = 3

registro = {}

for prompt in BANCO_DE_PROMPTS:
    exitos = 0
    for intento in range(INTENTOS):
        url, body = armar_peticion(
            prompt["ejemplo_usuario"],
            prompt["system_instruction"],
            prompt.get("response_schema"),
        )
        respuesta = enviar_peticion(url, body)
        texto = extraer_texto(respuesta)
        try:
            datos = parsear_respuesta_json(texto)
            if not all(clave in datos for clave in prompt["claves_esperadas"]):
                raise ValueError("La respuesta no tiene la estructura esperada.")
            exitos += 1
        except ValueError as error:
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(1)
    print(f"{prompt['nombre']}: {exitos}/{INTENTOS} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": INTENTOS, "ultima_salida": texto}

with open(RAIZ / "prompts" / "registro_resultados.json", "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)
