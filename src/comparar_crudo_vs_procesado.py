"""Compara 3 respuestas reales del cliente contra una referencia, antes y después del pipeline."""
from cliente import consultar_modelo
from pipeline_texto import procesar_texto

SISTEMA = "Responde en una sola frase corta, en español."
CASOS = [
    ("¿Qué es una pyme?", "Una pyme es una pequeña y mediana empresa."),
    ("¿Cuál es la capital de la Región del Biobío?", "La capital de la Región del Biobío es Concepción."),
    ("¿Qué es una boleta electrónica en Chile?", "La boleta electrónica es un documento tributario emitido al consumidor final y enviado al SII."),
]


def coincidencia(referencia, respuesta):
    comunes = set(referencia) & set(respuesta)
    return len(comunes) / len(set(referencia)) if referencia else 0.0


if __name__ == "__main__":
    for numero, (consulta, referencia) in enumerate(CASOS, start=1):
        respuesta = consultar_modelo(consulta, SISTEMA)
        print(f"[Caso {numero}] Consulta: {consulta}")
        print(f"[Caso {numero}] Referencia: {referencia}")
        print(f"[Caso {numero}] Respuesta: {respuesta}")
        print(f"[Caso {numero}] Coincidencia texto crudo: {coincidencia(referencia.split(), respuesta.split()):.1%}")
        print(f"[Caso {numero}] Coincidencia texto procesado: {coincidencia(procesar_texto(referencia), procesar_texto(respuesta)):.1%}\n")
