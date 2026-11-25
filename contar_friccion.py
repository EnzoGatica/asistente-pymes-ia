"""Cuenta las fricciones de docs/diario_de_friccion.md por sección y revisa que el README las tenga.

Uso:
    python contar_friccion.py [--readme README.md]
Cada fricción del diario es una línea "- [Sección] qué pasó".
"""
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DIARIO = Path("docs/diario_de_friccion.md")


def normal(texto):
    sin_tildes = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower().strip()


def secciones(texto):
    """{título normalizado: cuerpo} de cada sección de nivel 2."""
    partes = re.split(r"(?m)^## ", texto)[1:]
    resultado = {}
    for parte in partes:
        titulo, _, cuerpo = parte.partition("\n")
        resultado.setdefault(normal(titulo), cuerpo)
    return resultado


def fricciones():
    texto = DIARIO.read_text(encoding="utf-8")
    return re.findall(r"(?m)^- \[([^\]]+)\] (.+)$", texto)


def main(argumentos):
    conteo = Counter(seccion for seccion, _ in fricciones())
    for seccion, n in conteo.most_common():
        print(f"{n:3} {seccion}")
    print(f"\n{sum(conteo.values())} fricciones en {len(conteo)} secciones")
    if "--readme" in argumentos:
        ruta = Path(argumentos[argumentos.index("--readme") + 1])
        titulos = list(secciones(ruta.read_text(encoding="utf-8")))
        faltan = [s for s in conteo if not any(normal(s) in t for t in titulos)]
        for s in faltan:
            print(f"FALTA la seccion {s}")
        if not faltan:
            print(f"{ruta} tiene las {len(conteo)} secciones del diario")
        return 1 if faltan else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
