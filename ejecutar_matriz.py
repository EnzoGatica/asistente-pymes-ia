"""Ejecuta la Matriz de Pruebas contra el servicio y escribe su registro.

Uso:
    python ejecutar_matriz.py [--matriz matriz_pruebas] [--url http://127.0.0.1:8000] [--escribir]
Sin --url usa el servicio en memoria (TestClient) con la lógica real: necesita OPENAI_API_KEY en .env.
"""
import hashlib
import importlib
import json
import sys
import time
from datetime import date
from pathlib import Path

CLASIFICACIONES = {"defecto", "limitacion", "escenario mal escrito"}


def valor(argumentos, opcion, por_omision=None):
    if opcion in argumentos:
        i = argumentos.index(opcion)
        if i + 1 < len(argumentos):
            return argumentos[i + 1]
    return por_omision


def cargar(nombre):
    return importlib.import_module(nombre).MATRIZ


def registro_de(nombre):
    return Path("docs") / f"{nombre}.md"


def huella(matriz):
    texto = json.dumps(matriz, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def abrir_cliente(url=None):
    if url:
        import httpx2

        return httpx2.Client(base_url=url, timeout=30)
    from fastapi.testclient import TestClient

    from servicio.main import app

    return TestClient(app, raise_server_exceptions=False)


def motivos_de_falla(esperado, respuesta):
    motivos = []
    if respuesta.status_code != esperado["estado"]:
        motivos.append(f"estado {respuesta.status_code}, se esperaba {esperado['estado']}")
    for texto in esperado.get("contiene", []):
        if texto not in respuesta.text:
            motivos.append(f"falta {texto!r}")
    for texto in esperado.get("no_contiene", []):
        if texto in respuesta.text:
            motivos.append(f"no debia aparecer {texto!r}")
    if "fuentes" in esperado:
        try:
            fuentes = respuesta.json().get("fuentes")
        except ValueError:
            fuentes = None
        if fuentes != esperado["fuentes"]:
            motivos.append(f"fuentes {fuentes}, se esperaba {esperado['fuentes']}")
    return motivos


def ejecutar(cliente, matriz):
    resultados = []
    for e in matriz:
        p = e["peticion"]
        inicio = time.perf_counter()
        r = cliente.request(p["metodo"], p["ruta"], json=p.get("json"))
        motivos = motivos_de_falla(e["esperado"], r)
        resultados.append({
            "id": e["id"], "tipo": e["tipo"], "estado": r.status_code,
            "ms": round((time.perf_counter() - inicio) * 1000),
            "resultado": "FALLA" if motivos else "PASA", "motivos": motivos,
            "hallazgo": e.get("hallazgo"),
        })
    return resultados


def describir(e):
    p = e["peticion"]
    texto = f"{p['metodo']} {p['ruta']}"
    if "json" in p:
        cuerpo = json.dumps(p["json"], ensure_ascii=False)
        texto += " " + (cuerpo if len(cuerpo) <= 40 else cuerpo[:40] + "...")
    return texto.replace("|", "/")


def esperado_en_texto(x):
    partes = [str(x["estado"])]
    partes += [f"contiene {t!r}" for t in x.get("contiene", [])]
    partes += [f"no contiene {t!r}" for t in x.get("no_contiene", [])]
    if "fuentes" in x:
        partes.append(f"fuentes {x['fuentes']}")
    return "; ".join(partes).replace("|", "/")


def escribir(nombre, matriz, resultados):
    cumplidos = sum(r["resultado"] == "PASA" for r in resultados)
    lineas = [
        "# Matriz de Pruebas", "",
        f"Fecha: {date.today()}",
        f"Huella de la matriz: {huella(matriz)}",
        f"Escenarios: {cumplidos} de {len(resultados)} cumplidos", "",
        "| ID | Tipo | Escenario | Peticion | Esperado | Cubre | Resultado | Hallazgo |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for e, r in zip(matriz, resultados):
        h = r["hallazgo"]
        hallazgo = f"{h['clasificacion']}: {h['decision']}" if h else ""
        lineas.append(
            f"| {e['id']} | {e['tipo']} | {e['escenario']} | `{describir(e)}` | {esperado_en_texto(e['esperado'])} "
            f"| {', '.join(e['cubre'])} | {r['resultado']} | {hallazgo} |"
        )
    ruta = registro_de(nombre)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    return ruta


def main(argumentos):
    nombre = valor(argumentos, "--matriz", "matriz_pruebas")
    matriz = cargar(nombre)
    resultados = ejecutar(abrir_cliente(valor(argumentos, "--url")), matriz)
    for r in resultados:
        print(f"{r['resultado']:5} {r['id']} {r['tipo']} {r['estado']} {r['ms']} ms")
        for m in r["motivos"]:
            print(f"      -> {m}")
    cumplidos = sum(r["resultado"] == "PASA" for r in resultados)
    print(f"\nEscenarios: {cumplidos} de {len(resultados)} cumplidos")
    if "--escribir" in argumentos:
        print(f"Registro escrito en {escribir(nombre, matriz, resultados)}")
    return 0 if cumplidos == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
