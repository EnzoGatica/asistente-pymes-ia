"""Ejecuta escenarios.py contra la solución en marcha (docker compose up -d) y dice qué falla y por qué.

Uso:
    python ejecutar_escenarios.py
    python ejecutar_escenarios.py --dos-veces    (comprueba que dos corridas den lo mismo)
"""
import sys
import time

import httpx2

from escenarios import ESCENARIOS

DESTINOS = {"api": "http://127.0.0.1:8000", "interfaz": "http://127.0.0.1:8080"}


def motivos_de(escenario, respuesta):
    motivos = []
    if respuesta.status_code != escenario["estado"]:
        motivos.append(f"estado {respuesta.status_code}, se esperaba {escenario['estado']}")
    texto = respuesta.text
    for fragmento in escenario.get("contiene", []):
        if fragmento not in texto:
            motivos.append(f"falta {fragmento!r}")
    for fragmento in escenario.get("no_contiene", []):
        if fragmento in texto:
            motivos.append(f"aparece {fragmento!r}")
    if "fuentes_incluye" in escenario or escenario.get("fuentes_vacias"):
        try:
            fuentes = respuesta.json().get("fuentes")
        except ValueError:
            fuentes = None
        if "fuentes_incluye" in escenario and escenario["fuentes_incluye"] not in (fuentes or []):
            motivos.append(f"fuentes {fuentes} sin {escenario['fuentes_incluye']}")
        if escenario.get("fuentes_vacias") and fuentes != []:
            motivos.append(f"fuentes {fuentes}, se esperaban vacías")
    return motivos


def correr():
    resultados = []
    with httpx2.Client(timeout=30) as cliente:
        for e in ESCENARIOS:
            url = DESTINOS[e["destino"]] + e["ruta"]
            inicio = time.perf_counter()
            try:
                r = cliente.request(e["metodo"], url, params=e.get("params"), json=e.get("json"))
                motivos = motivos_de(e, r)
            except httpx2.HTTPError as error:
                motivos = [f"sin respuesta: {type(error).__name__}"]
            resultados.append({"id": e["id"], "categoria": e["categoria"], "descripcion": e["descripcion"],
                               "segundos": round(time.perf_counter() - inicio, 2), "motivos": motivos})
    return resultados


def firma(resultados):
    return tuple((r["id"], not r["motivos"]) for r in resultados)


def informe(resultados):
    for r in resultados:
        estado = "PASA " if not r["motivos"] else "FALLA"
        detalle = "; ".join(r["motivos"]) or f"{r['segundos']} s"
        print(f"{estado} {r['id']} [{r['categoria']}] {r['descripcion']} -> {detalle}")
    cumplidos = sum(1 for r in resultados if not r["motivos"])
    print(f"\n{cumplidos} de {len(resultados)} escenarios cumplidos")
    return cumplidos == len(resultados)


if __name__ == "__main__":
    primera = correr()
    ok = informe(primera)
    if "--dos-veces" in sys.argv:
        igual = firma(correr()) == firma(primera)
        print("segunda corrida:", "igual a la primera" if igual else "DISTINTA de la primera")
        ok = ok and igual
    sys.exit(0 if ok else 1)
