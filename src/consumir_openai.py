import os
import requests
from dotenv import load_dotenv

load_dotenv()

URL_CHAT = "https://api.openai.com/v1/chat/completions"
MODELO = "gpt-4.1-nano"

# USD por 1 millón de tokens (https://openai.com/api/pricing, revisado el 22-10-2026)
PRECIOS = {
    "gpt-4.1-nano": {"entrada": 0.10, "salida": 0.40},
    "gpt-4.1-mini": {"entrada": 0.40, "salida": 1.60},
}


def armar_peticion(pregunta, modelo=MODELO):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    body = {
        "model": modelo,
        "messages": [{"role": "user", "content": pregunta}],
    }
    return URL_CHAT, body


def enviar_peticion(url, body):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY: copia .env.example como .env y completa tu llave.")
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        respuesta = requests.post(url, headers=headers, json=body, timeout=30)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    try:
        datos = respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado (no es JSON).")
    if respuesta.status_code != 200:
        mensaje = datos.get("error", {}).get("message", "sin detalle")
        raise RuntimeError(f"El servicio respondió con error {respuesta.status_code}: {mensaje}")
    return datos


def extraer_texto(datos):
    try:
        return datos["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("La respuesta no trae el texto generado en choices[0].message.content.")


def calcular_costo(datos, modelo=MODELO):
    uso = datos.get("usage", {})
    precio = PRECIOS[modelo]
    entrada = uso.get("prompt_tokens", 0)
    salida = uso.get("completion_tokens", 0)
    return (entrada * precio["entrada"] + salida * precio["salida"]) / 1_000_000


def obtener_respuesta(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos), calcular_costo(datos)


if __name__ == "__main__":
    try:
        texto, costo = obtener_respuesta("Confirma en una frase corta que esta conexión funciona")
        print(texto)
        print(f"Costo de la petición: USD {costo:.8f}")
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
