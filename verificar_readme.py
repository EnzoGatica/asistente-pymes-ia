"""Verifica que el README sea completo y que no mienta.

Uso:
    python verificar_readme.py
Se ejecuta desde la raiz del repositorio.
"""

import re
import subprocess
import sys
import textwrap
from pathlib import Path

import buscar_secretos
from contar_friccion import normal, secciones

README = Path("README.md")
SECCIONES = {
    "requisitos": "Requisitos",
    "instalacion": "Instalación",
    "configuracion": "Configuración",
    "arrancar": "Cómo arrancar",
    "comprobar": "Cómo comprobar",
    "pruebas": "Pruebas",
    "decisiones": "Decisiones",
    "limitaciones": "Limitaciones",
    "estructura": "Estructura",
    "problemas": "Problemas frecuentes",
}
MODULOS = {"pytest", "venv", "uvicorn"}
PERMITIDAS = {".env", ".venv"}
EXTENSIONES = (".py", ".md", ".yaml", ".txt", ".png")


def cuerpo_de(texto, clave):
    for titulo, cuerpo in secciones(texto).items():
        if clave in titulo:
            return cuerpo
    return ""


def candidatos(texto):
    """Comandos del README: lineas de bloques y codigo en linea."""
    comandos = []
    for bloque in re.findall(r"```[^\n]*\n(.*?)```", texto, re.S):
        comandos += [l.strip() for l in bloque.splitlines()]
    sin_bloques = re.sub(r"```.*?```", "", texto, flags=re.S)
    comandos += re.findall(r"`([^`\n]+)`", sin_bloques)
    return [c for c in comandos if c and not c.startswith("#")]


def secciones_presentes(texto):
    titulos = list(secciones(texto))
    faltan = [
        nombre for clave, nombre in SECCIONES.items()
        if not any(clave in t for t in titulos)
    ]
    if faltan:
        return False, "faltan las secciones: " + ", ".join(faltan)
    return True, f"{len(SECCIONES)} secciones presentes"


def variables(texto):
    declaradas = set(
        re.findall(
            r"^([A-Z][A-Z0-9_]*)=", Path(".env.example").read_text(
                encoding="utf-8"
            ), re.M,
        )
    )
    leidas = set()
    for ruta in Path("servicio").glob("*.py"):
        leidas |= set(
            re.findall(
                r'environ.get\("([A-Z0-9_]+)"',
                ruta.read_text(encoding="utf-8"),
            )
        )
    cuerpo = cuerpo_de(texto, "configuracion")
    lineas = {}
    for n in re.findall(r"`([A-Z][A-Z0-9_]{2,})`", cuerpo):
        lineas[n] = next(
            l for l in cuerpo.splitlines() if f"`{n}`" in l
        )
    problemas = []
    for n in sorted(leidas - declaradas):
        problemas.append(
            f"{n} se lee en el codigo y no esta en .env.example"
        )
    for n in sorted(declaradas - set(lineas)):
        problemas.append(f"{n} no esta documentada en el README")
    for n in sorted(set(lineas) - declaradas):
        problemas.append(f"{n} esta en el README y no existe")
    etiqueta = re.compile(r"\((secreto|configuracion)\)")
    for n, linea in sorted(lineas.items()):
        if not etiqueta.search(normal(linea)):
            problemas.append(f"{n} no dice si es secreto o dato")
    if problemas:
        return False, "; ".join(problemas)
    return True, f"{len(declaradas)} variables, todas documentadas"


def comandos_validos(texto):
    problemas, vistos = [], 0
    for c in candidatos(texto):
        m = re.match(r"python3? +(-m +(\w+)|(\S+\.py))", c)
        if m:
            vistos += 1
            if m.group(2) and m.group(2) not in MODULOS:
                problemas.append(f"modulo desconocido: {c}")
            if m.group(3) and not Path(m.group(3)).is_file():
                problemas.append(f"no existe {m.group(3)}")
        m = re.match(r"cp +(\S+) +\S+$", c)
        if m:
            vistos += 1
            if not Path(m.group(1)).is_file():
                problemas.append(f"no existe {m.group(1)}")
        m = re.match(r"pip install -r +(\S+)", c)
        if m:
            vistos += 1
            if not Path(m.group(1)).is_file():
                problemas.append(f"no existe {m.group(1)}")
    if vistos == 0:
        return False, "el README no trae ningun comando que ejecutar"
    if problemas:
        return False, "; ".join(sorted(set(problemas)))
    return True, f"{vistos} comandos apuntan a archivos que existen"


def rutas_validas(texto):
    problemas, vistas = [], set()
    for c in re.findall(r"`([^`\s]+)`", texto):
        if c.startswith(("/", "http")) or c in PERMITIDAS:
            continue
        if re.search(r"[{}*<>=]", c):
            continue
        if "/" in c or c.endswith(EXTENSIONES):
            vistas.add(c)
            if not Path(c.rstrip("/")).exists():
                problemas.append(f"no existe {c}")
    if not vistas:
        return False, "el README no cita ningun archivo del proyecto"
    if problemas:
        return False, "; ".join(sorted(set(problemas)))
    return True, f"{len(vistas)} rutas citadas, todas existen"


def puertos(texto):
    compose = Path("compose.yaml").read_text(encoding="utf-8")
    reales = set(re.findall(r'"(\d+):\d+"', compose))
    citados = set(re.findall(r"127\.0\.0\.1:(\d+)", texto))
    problemas = []
    for p in sorted(reales - citados):
        problemas.append(f"el puerto {p} de compose.yaml no esta")
    for p in sorted(citados - reales):
        problemas.append(f"el README usa {p} y compose.yaml no")
    if problemas:
        return False, "; ".join(problemas)
    return True, "puertos del README: " + ", ".join(sorted(reales))


def sin_secretos(texto):
    hallazgos = []
    for n, linea in enumerate(texto.splitlines(), start=1):
        if buscar_secretos.CLAVE_GOOGLE.search(linea):
            hallazgos.append(f"linea {n}: clave")
        if buscar_secretos.ASIGNACION.search(linea):
            hallazgos.append(f"linea {n}: valor de secreto")
    if hallazgos:
        return False, "; ".join(hallazgos)
    return True, "ninguna clave ni valor de secreto"


def version_de_python(texto):
    docker = Path("Dockerfile").read_text(encoding="utf-8")
    imagen = re.search(r"FROM python:(\d+\.\d+)", docker).group(1)
    citada = re.findall(r"Python (\d+\.\d+)", texto)
    if imagen not in citada:
        dice = ", ".join(citada) or "ninguna"
        return False, f"la imagen usa {imagen}; el README dice {dice}"
    return True, f"el README y la imagen coinciden: Python {imagen}"


def pruebas_ejecutan(texto):
    if "python -m pytest -q" not in texto:
        return False, "el README no dice como ejecutar las pruebas"
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    ultima = r.stdout.strip().splitlines()[-1] if r.stdout else ""
    if r.returncode != 0:
        return False, f"pytest termina con {r.returncode}: {ultima}"
    return True, "el comando de pruebas del README termina bien"


def main():
    texto = README.read_text(encoding="utf-8")
    comprobaciones = [
        ("README-1", "secciones", secciones_presentes(texto)),
        ("README-2", "variables", variables(texto)),
        ("README-3", "comandos", comandos_validos(texto)),
        ("README-4", "rutas", rutas_validas(texto)),
        ("README-5", "puertos", puertos(texto)),
        ("README-6", "secretos", sin_secretos(texto)),
        ("README-7", "version de Python", version_de_python(texto)),
        ("README-8", "pruebas", pruebas_ejecutan(texto)),
    ]
    cumplidas = 0
    for id_, nombre, (ok, evidencia) in comprobaciones:
        cumplidas += ok
        marca = "PASA " if ok else "FALLA"
        linea = f"{marca} {id_} {nombre} -> {evidencia}"
        print(textwrap.fill(linea, 70, subsequent_indent="      "))
    total = len(comprobaciones)
    print(f"\n{cumplidas} de {total} comprobaciones cumplidas")
    return 0 if cumplidas == total else 1


if __name__ == "__main__":
    sys.exit(main())
