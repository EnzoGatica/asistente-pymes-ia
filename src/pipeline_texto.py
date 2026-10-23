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


def calcular_precision_cobertura_f1(tokens_referencia: list[str], tokens_respuesta: list[str]) -> dict:
    """Coincidencia por palabras contando repeticiones (Counter), no solo presencia (set)."""
    comunes = sum((Counter(tokens_referencia) & Counter(tokens_respuesta)).values())
    precision = comunes / len(tokens_respuesta) if tokens_respuesta else 0.0
    cobertura = comunes / len(tokens_referencia) if tokens_referencia else 0.0
    f1 = 2 * precision * cobertura / (precision + cobertura) if precision + cobertura else 0.0
    return {"precision": round(precision, 2), "cobertura": round(cobertura, 2), "f1": round(f1, 2)}


def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict:
    return calcular_precision_cobertura_f1(procesar_texto(texto_referencia), procesar_texto(texto_respuesta))


def resumir_metricas(resultados: list[dict]) -> dict:
    if not resultados:
        return {"precision_promedio": 0, "cobertura_promedio": 0, "f1_promedio": 0}
    n = len(resultados)
    return {
        "precision_promedio": round(sum(r["precision"] for r in resultados) / n, 2),
        "cobertura_promedio": round(sum(r["cobertura"] for r in resultados) / n, 2),
        "f1_promedio": round(sum(r["f1"] for r in resultados) / n, 2),
    }
