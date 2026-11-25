import json
import re
import subprocess
import sys
from pathlib import Path

SECCIONES = (
    "Requisitos",
    "Configuración",
    "Cómo arrancar",
    "Cómo comprobar que funciona",
    "Cómo detener",
    "Problemas frecuentes",
)
CRITERIOS = [f"VC-{n}" for n in range(1, 7)]
ESTADOS = ("PASA", "FALLA")
DECISIONES = ("aceptado", "rechazado", "aplazado")
RUTA_REVISION = Path("docs/verificacion_cruzada.md")


def leer(ruta):
    ruta = Path(ruta)
    return ruta.read_text(encoding="utf-8") if ruta.exists() else None


def configuracion():
    r = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    return json.loads(r.stdout) if r.returncode == 0 else None


def composicion_valida():
    datos = configuracion()
    if datos is None:
        return False, "docker compose config no pudo leer compose.yaml"
    servicios = datos["services"]
    if len(servicios) < 2:
        return False, f"hay {len(servicios)} servicio(s) y se piden 2"
    con_latest = [
        n
        for n, s in servicios.items()
        if s.get("image", "").endswith(":latest")
    ]
    if con_latest:
        return False, f"imagen con latest en: {con_latest}"
    dependencias = [
        n for n, s in servicios.items() if "depends_on" in s
    ]
    if not dependencias:
        return False, "ningun servicio declara depends_on"
    return True, f"servicios {sorted(servicios)} con depends_on"


def readme_con_secciones():
    texto = leer("README.md")
    if texto is None:
        return False, "no existe README.md"
    titulos = re.findall(r"^## (.+)$", texto, re.MULTILINE)
    faltan = [s for s in SECCIONES if s not in titulos]
    if faltan:
        return False, f"faltan secciones: {faltan}"
    return True, f"las {len(SECCIONES)} secciones estan"


def variables_documentadas():
    ejemplo, readme = leer(".env.example"), leer("README.md")
    if ejemplo is None or readme is None:
        return False, "falta .env.example o README.md"
    nombres = re.findall(r"^([A-Z][A-Z0-9_]*)=", ejemplo, re.MULTILINE)
    sin_doc = [n for n in nombres if n not in readme]
    if sin_doc:
        return False, f"variables sin explicar en el README: {sin_doc}"
    return True, f"el README explica {nombres}"


def archivos_existentes():
    readme = leer("README.md")
    if readme is None:
        return False, "no existe README.md"
    # nombres entre comillas invertidas con extensión de archivo conocida
    patron = r"`([\w./-]+\.(?:py|md|yaml|yml|txt|example|json))`"
    citados = sorted(set(re.findall(patron, readme)))
    faltan = [a for a in citados if not Path(a).exists()]
    if faltan:
        return False, f"el README cita archivos que no existen: {faltan}"
    return True, f"existen los {len(citados)} archivos que cita"


def puertos_documentados():
    datos = configuracion()
    readme = leer("README.md")
    if datos is None or readme is None:
        return False, "falta compose.yaml o README.md"
    puertos = sorted(
        {
            str(p["published"])
            for s in datos["services"].values()
            for p in s.get("ports", [])
        }
    )
    sin_doc = [p for p in puertos if p not in readme]
    if sin_doc:
        return False, f"puertos sin documentar: {sin_doc}"
    return True, f"el README documenta los puertos {puertos}"


def revision_valida():
    texto = leer(RUTA_REVISION)
    if texto is None:
        return False, f"no existe {RUTA_REVISION}"
    errores = []
    for campo in ("Revisor", "Repositorio revisado", "Fecha"):
        if not re.search(rf"^{campo}: .+$", texto, re.MULTILINE):
            errores.append(f"falta '{campo}:'")
    if "Se siguió únicamente: README.md" not in texto:
        errores.append("falta 'Se siguió únicamente: README.md'")
    estados = {}
    for c in CRITERIOS:
        m = re.search(rf"^- {c} \([^)]*\): (\w+) - .+$", texto, re.M)
        if not m or m.group(1) not in ESTADOS:
            errores.append(f"{c} sin resultado PASA o FALLA")
        else:
            estados[c] = m.group(1)
    hallazgos = re.findall(
        r"^- Hallazgo \d+ \((VC-\d)\): .+\n  Decisión: (\w+) - .+$",
        texto,
        re.MULTILINE,
    )
    for _, decision in hallazgos:
        if decision not in DECISIONES:
            errores.append(f"decision invalida: {decision}")
    citados = {c for c, _ in hallazgos}
    for c, estado in estados.items():
        if estado == "FALLA" and c not in citados:
            errores.append(f"{c} falla y no tiene hallazgo")
    if "Sin hallazgos" not in texto and not hallazgos:
        errores.append("sin hallazgos ni la frase 'Sin hallazgos'")
    if errores:
        return False, "; ".join(errores)
    return (
        True,
        f"{len(estados)} criterios y {len(hallazgos)} hallazgos",
    )


def sin_secretos():
    r = subprocess.run(
        [sys.executable, "buscar_secretos.py"],
        capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    ultima = r.stdout.strip().splitlines()[-1] if r.stdout else ""
    return r.returncode == 0, ultima or "buscar_secretos.py fallo"


COMPROBACIONES = [
    ("ENT-1", "composicion con dos servicios", composicion_valida),
    ("ENT-2", "README con las secciones", readme_con_secciones),
    ("ENT-3", "variables explicadas", variables_documentadas),
    ("ENT-4", "archivos citados existen", archivos_existentes),
    ("ENT-5", "puertos documentados", puertos_documentados),
    ("ENT-6", "verificacion cruzada registrada", revision_valida),
    ("ENT-7", "sin secretos", sin_secretos),
]


def ejecutar():
    cumplidas = 0
    for id_, descripcion, prueba in COMPROBACIONES:
        try:
            ok, evidencia = prueba()
        except Exception as error:
            ok, evidencia = False, f"error: {error!r}"
        estado = "PASA " if ok else "FALLA"
        print(f"{estado} {id_} {descripcion} -> {evidencia}")
        cumplidas += 1 if ok else 0
    total = len(COMPROBACIONES)
    print(f"\n{cumplidas} de {total} comprobaciones cumplidas")
    return cumplidas == total


if __name__ == "__main__":
    sys.exit(0 if ejecutar() else 1)
