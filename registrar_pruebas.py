import json
import os
import sys
from datetime import date

import httpx2

from casos import CASOS, ejecutar_caso

RUTA = "docs/registro_pruebas.md"
ESTADOS_OBLIGATORIOS = (404, 405, 422)
COLUMNAS = (
    "Caso", "Descripción", "Petición",
    "Esperado", "Obtenido", "Resultado",
)


def verificar_cobertura(casos):
    errores = []
    validos = [c for c in casos if c["id"].startswith("V-")]
    invalidos = [c for c in casos if c["id"].startswith("I-")]
    if len(validos) < 3:
        errores.append(f"hay {len(validos)} casos validos y se piden 3")
    if len(invalidos) < 5:
        errores.append(
            f"hay {len(invalidos)} casos invalidos y se piden 5"
        )
    esperados = {c["estado"] for c in invalidos}
    for estado in ESTADOS_OBLIGATORIOS:
        if estado not in esperados:
            errores.append(
                f"ningun caso invalido espera el estado {estado}"
            )
    return errores


def describir(caso):
    cuerpo = caso.get("contenido")
    if cuerpo is None and "json" in caso:
        cuerpo = json.dumps(caso["json"], ensure_ascii=False)
    texto = f"{caso['metodo']} {caso['ruta']}"
    if cuerpo:
        corto = cuerpo if len(cuerpo) <= 40 else cuerpo[:40] + "..."
        texto += f" {corto}"
    return texto.replace("|", "/")


def registrar(base_url):
    filas = []
    # timeout de 30 s: las consultas reales pasan por OpenAI
    with httpx2.Client(base_url=base_url, timeout=30) as cliente:
        for caso in CASOS:
            ok, estado, _ = ejecutar_caso(cliente, caso)
            filas.append((caso, ok, estado))
    cumplidos = sum(1 for _, ok, _ in filas if ok)
    lineas = [
        "# Registro de pruebas de la API",
        f"Fecha: {date.today()}",
        f"Servicio probado: {base_url} (cliente: httpx2)",
        f"Resultado: {cumplidos} de {len(filas)} casos cumplidos",
        "",
        "| " + " | ".join(COLUMNAS) + " |",
        "|" + "---|" * len(COLUMNAS),
    ]
    for caso, ok, estado in filas:
        veredicto = "PASA" if ok else "FALLA"
        lineas.append(
            f"| {caso['id']} | {caso['descripcion']} "
            f"| {describir(caso)} | {caso['estado']} "
            f"| {estado} | {veredicto} |"
        )
    os.makedirs("docs", exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")
    return cumplidos, len(filas)


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    errores = verificar_cobertura(CASOS)
    for error in errores:
        print("ERROR:", error)
    if errores:
        sys.exit(1)
    try:
        cumplidos, total = registrar(base)
    except httpx2.ConnectError:
        sys.exit(f"No se pudo conectar a {base}. Arranca el servicio.")
    print(f"Registro escrito en {RUTA}: {cumplidos} de {total} casos")
    sys.exit(0 if cumplidos == total else 1)
