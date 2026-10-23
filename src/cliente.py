"""Cliente modular: un solo punto de entrada (consultar_modelo) con reintento y clasificación de errores."""
import logging
import os
import time

import requests

from consumir_openai import MODELO, armar_peticion, calcular_costo, extraer_texto

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cliente")

costo_total_sesion = 0.0


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


def con_reintento(funcion, intentos=3, espera_base=1):
    """Reintenta solo TimeoutError (429, 5xx, red) con backoff exponencial: 1 s, 2 s, 4 s..."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = espera_base * 2 ** (intento - 1)
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando en {espera} s...")
            time.sleep(espera)


def registrar_costo(respuesta, modelo=MODELO):
    global costo_total_sesion
    costo = calcular_costo(respuesta, modelo)
    costo_total_sesion += costo
    uso = respuesta.get("usage", {})
    logger.info(
        "operacion modelo=%s tokens_entrada=%s tokens_salida=%s costo_usd=%.8f total_sesion_usd=%.8f",
        modelo, uso.get("prompt_tokens", 0), uso.get("completion_tokens", 0), costo, costo_total_sesion,
    )
    return costo


def consultar_modelo(pregunta: str, system_instruction: str = "", response_schema: dict | None = None) -> str:
    url, body = armar_peticion(pregunta, system_instruction, response_schema)
    try:
        respuesta = con_reintento(lambda: enviar_peticion(url, body))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        print(consultar_modelo("¿Cuál es la capital de Chile?"))
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"El servicio no respondió tras varios intentos: {error}")
