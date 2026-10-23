"""Pipeline de texto: limpieza, tokenización y métricas de coincidencia contra una referencia."""
import re
import string
from collections import Counter

PUNTUACION = string.punctuation + "¿¡«»“”‘’…–—"


def limpiar_texto(texto: str) -> str:
    sin_puntuacion = texto.lower().translate(str.maketrans(PUNTUACION, " " * len(PUNTUACION)))
    return re.sub(r"\s+", " ", sin_puntuacion).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    return tokenizar(limpiar_texto(texto))
