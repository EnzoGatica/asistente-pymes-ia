"""Cliente modular: un solo punto de entrada (consultar_modelo) con reintento y clasificación de errores."""
import os
import time

import requests

from consumir_openai import armar_peticion, extraer_texto


def enviar_peticion(url, body):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Falta OPENAI_API_KEY: copia .env.example como .env y completa tu llave.")
    try:
        respuesta = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=30)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise TimeoutError("El servicio no respondió (error de conexión o tiempo de espera agotado).")
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu OPENAI_API_KEY.")
    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError(f"Límite de uso o falla temporal del proveedor (HTTP {respuesta.status_code}).")
    if respuesta.status_code != 200:
        raise RuntimeError(f"El servicio rechazó la petición (HTTP {respuesta.status_code}).")
    return respuesta.json()


def con_reintento(funcion, intentos=3, espera=2):
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera)


def consultar_modelo(pregunta: str, system_instruction: str = "", response_schema: dict | None = None) -> str:
    url, body = armar_peticion(pregunta, system_instruction, response_schema)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, body))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        print(consultar_modelo("¿Cuál es la capital de Chile?"))
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"El servicio no respondió tras varios intentos: {error}")
