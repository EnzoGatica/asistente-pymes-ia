import os
import requests
from dotenv import load_dotenv

load_dotenv()

URL_CHAT = "https://api.openai.com/v1/chat/completions"
MODELO = "gpt-4.1-nano"


def armar_peticion(pregunta):
    body = {
        "model": MODELO,
        "messages": [{"role": "user", "content": pregunta}],
    }
    return URL_CHAT, body


def enviar_peticion(url, body):
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    respuesta = requests.post(url, headers=headers, json=body)
    return respuesta.json()


def extraer_texto(datos):
    return datos["choices"][0]["message"]["content"]


def obtener_respuesta(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    print(obtener_respuesta("Confirma en una frase corta que esta conexión funciona"))
