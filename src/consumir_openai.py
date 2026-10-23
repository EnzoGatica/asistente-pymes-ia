import os
import requests
from dotenv import load_dotenv

load_dotenv()


def obtener_respuesta(pregunta):
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    body = {
        "model": "gpt-4.1-nano",
        "messages": [{"role": "user", "content": pregunta}],
    }
    respuesta = requests.post(url, headers=headers, json=body)
    datos = respuesta.json()
    return datos["choices"][0]["message"]["content"]


print(obtener_respuesta("Confirma en una frase corta que esta conexión funciona"))
