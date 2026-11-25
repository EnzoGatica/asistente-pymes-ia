"""Escribe la zona automática de docs/registro_ejecucion.md a partir de una corrida real.

Uso (con la solución arriba: docker compose up -d --wait):
    python registrar_ejecucion.py
Solo reemplaza lo que está entre las marcas AUTO; las secciones manuales de abajo se conservan.
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import httpx2

import ejecutar_escenarios as ee

REGISTRO = Path("docs/registro_ejecucion.md")
INICIO, FIN = "<!-- AUTO:INICIO -->", "<!-- AUTO:FIN -->"
MANUAL = """
## Qué se observó

[COMPLETAR]

## Qué no se probó

[COMPLETAR]

## Siguiente paso

[COMPLETAR]
"""


def comando(*args):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def commit_del_codigo():
    _, hash_ = comando("git", "rev-parse", "--short", "HEAD")
    _, cambios = comando("git", "status", "--porcelain")
    de_codigo = [ln for ln in cambios.splitlines() if not ln[3:].startswith("docs/")]
    return hash_, "sin cambios" if not de_codigo else f"con {len(de_codigo)} archivos sin confirmar"


def pruebas_automaticas():
    _, salida = comando(sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider")
    resumen = salida.splitlines()[-1] if salida else ""
    pasan = re.search(r"(\d+) passed", resumen)
    fallan = re.search(r"(\d+) failed", resumen)
    return int(pasan.group(1)) if pasan else 0, int(fallan.group(1)) if fallan else 0


def componentes():
    salud = httpx2.get(ee.DESTINOS["api"] + "/salud", timeout=5).json()
    from servicio_rag import MODELO  # noqa: PLC0415  (mismo valor que usa la imagen)

    modelo = "real" if salud.get("modelo") == "configurado" else "sin clave"
    return [
        ("Modelo", modelo, f"OpenAI {MODELO}"),
        ("Recuperación", "real", "Chroma con embeddings text-embedding-3-small sobre corpus/"),
        ("API", "real", f"FastAPI en contenedor, entorno {salud.get('entorno')}"),
        ("Interfaz", "real", "FastAPI en contenedor, llama a la API por la red de Compose"),
        ("Pedidos", "simulado", "datos de src/negocio.py"),
    ]


def zona_automatica():
    resultados = ee.correr()
    cumplidos = sum(1 for r in resultados if not r["motivos"])
    pasan, fallan = pruebas_automaticas()
    hash_, estado = commit_del_codigo()
    lineas = [
        INICIO,
        "# Registro de la ejecución completa",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Fecha | {datetime.now():%Y-%m-%d %H:%M} |",
        f"| Commit del código | {hash_} ({estado}) |",
        f"| Destinos | API {ee.DESTINOS['api']} e interfaz {ee.DESTINOS['interfaz']} |",
        "",
        f"Escenarios: {cumplidos} de {len(resultados)} cumplidos",
        "",
        f"Pruebas automáticas: {pasan} pasan, {fallan} fallan",
        "",
        "## Componentes",
        "",
        "| Componente | Modo | Detalle |",
        "|---|---|---|",
        *[f"| {c} | {modo} | {detalle} |" for c, modo, detalle in componentes()],
        "",
        "## Resultados por escenario",
        "",
        "| Escenario | Descripción | Resultado |",
        "|---|---|---|",
        *[f"| {r['id']} | {r['descripcion']} | {'pasa' if not r['motivos'] else 'falla'} |" for r in resultados],
        FIN,
    ]
    return "\n".join(lineas)


def main():
    auto = zona_automatica()
    if REGISTRO.exists():
        texto = REGISTRO.read_text(encoding="utf-8")
        resto = texto.split(FIN, 1)[1] if FIN in texto else MANUAL
    else:
        resto = MANUAL
    REGISTRO.write_text(auto + resto, encoding="utf-8", newline="\n")
    print(f"Zona automática de {REGISTRO} actualizada")


if __name__ == "__main__":
    main()
