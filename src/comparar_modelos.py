"""Compara dos modelos candidatos con peticiones reales: latencia, tokens y costo."""
import time

from consumir_openai import PRECIOS, armar_peticion, calcular_costo, enviar_peticion, extraer_texto

PREGUNTA = (
    "Soy dueño de una panadería en Tomé. Un cliente pregunta por WhatsApp si hacemos "
    "tortas para 30 personas con despacho a Dichato. Redacta una respuesta breve y amable."
)
REPETICIONES = 5


def medir(modelo):
    latencias, costos, tokens_salida = [], [], []
    for _ in range(REPETICIONES):
        url, body = armar_peticion(PREGUNTA, modelo)
        inicio = time.perf_counter()
        datos = enviar_peticion(url, body)
        latencias.append(time.perf_counter() - inicio)
        costos.append(calcular_costo(datos, modelo))
        tokens_salida.append(datos["usage"]["completion_tokens"])
        ultima = extraer_texto(datos)
    return {
        "latencia_promedio_s": sum(latencias) / REPETICIONES,
        "costo_promedio_usd": sum(costos) / REPETICIONES,
        "tokens_salida_promedio": sum(tokens_salida) / REPETICIONES,
        "ejemplo": ultima,
    }


if __name__ == "__main__":
    print(f"| Modelo | Precio entrada / salida (USD por 1M tokens) | Latencia promedio (s) | Tokens de salida promedio | Costo promedio por request (USD) | Costo por 1.000 requests (USD) |")
    print("|---|---|---|---|---|---|")
    ejemplos = {}
    for modelo in PRECIOS:
        r = medir(modelo)
        ejemplos[modelo] = r["ejemplo"]
        p = PRECIOS[modelo]
        print(f"| {modelo} | {p['entrada']:.2f} / {p['salida']:.2f} | {r['latencia_promedio_s']:.2f} | "
              f"{r['tokens_salida_promedio']:.0f} | {r['costo_promedio_usd']:.7f} | {r['costo_promedio_usd'] * 1000:.4f} |")
    for modelo, texto in ejemplos.items():
        print(f"\n### Respuesta de ejemplo de {modelo}\n\n{texto}")
