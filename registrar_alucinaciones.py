"""Ejecuta las sondas de alucinacion.py y escribe docs/registro_alucinaciones.md.

Uso:
    python registrar_alucinaciones.py [--escribir]
"""
import sys
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from servicio.main import app
from verificar_mitigaciones import contener_alucinaciones

REGISTRO = Path("docs/registro_alucinaciones.md")


def main(argumentos):
    filas = contener_alucinaciones(TestClient(app, raise_server_exceptions=False))
    for resultado, id_, nombre, detalle in filas:
        print(f"{resultado:6} {id_} {nombre}")
    if "--escribir" in argumentos:
        lineas = [
            "# Registro de alucinaciones", "",
            f"Fecha: {date.today()}",
            "Cada sonda hace que el modelo simulado responda algo que el contexto no respalda; "
            "contenida significa que la API devolvió el mensaje de sin información con fuentes vacías.", "",
            "| Sonda | Tipo | Resultado | Decisión |", "|---|---|---|---|",
            *[f"| {i} | {n.removeprefix('alucinacion: ')} | {r} | {d} |" for r, i, n, d in filas],
        ]
        REGISTRO.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
        print(f"\nRegistro escrito en {REGISTRO}")
    return 0 if all(r != "FALLA" for r, *_ in filas) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
