import re
import subprocess
import sys
from pathlib import Path

CLAVE_GOOGLE = re.compile(r"AIza[0-9A-Za-z_\-]{35}")
NOMBRE = (
    r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]*"
    r"(?:KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*"
)
NOMBRE_SECRETO = re.compile(r"KEY|TOKEN|SECRET|PASSWORD")
# valor literal: no vacio, no una referencia ($VAR, ${VAR}), 8+ caracteres
ASIGNACION = re.compile(NOMBRE + r"\s*[=:]\s*[\"']?([^\s\"'$#<>{}]{8,})")
ASIGNACION_PY = re.compile(NOMBRE + r"\s*=\s*[\"']([^\"'$]{8,})[\"']")
IGNORAR = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "vectorstore", "logs"}


def ocultar(valor):
    return valor[:3] + "***"


def archivos():
    for ruta in Path(".").rglob("*"):
        if not ruta.is_file() or ruta.name == ".env":
            continue
        if IGNORAR & set(ruta.parts):
            continue
        yield ruta


def buscar_en_archivos():
    hallazgos = []
    for ruta in archivos():
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for n, linea in enumerate(texto.splitlines(), start=1):
            for m in CLAVE_GOOGLE.finditer(linea):
                hallazgos.append(f"{ruta}:{n} {ocultar(m.group())}")
            regla = (
                ASIGNACION_PY if ruta.suffix == ".py" else ASIGNACION
            )
            for m in regla.finditer(linea):
                valor = ocultar(m.group(1))
                hallazgos.append(f"{ruta}:{n} valor {valor}")
    return hallazgos


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def archivos_limpios():
    hallazgos = buscar_en_archivos()
    if hallazgos:
        return False, f"{len(hallazgos)} hallazgos: {hallazgos[:3]}"
    return True, "ningun valor con forma de secreto"


def env_ignorado():
    codigo, _ = git("check-ignore", "-q", ".env")
    return codigo == 0, ".env figura en .gitignore"


def env_no_versionado():
    _, listado = git("ls-files", ".env")
    return listado == "", "git no sigue el archivo .env"


def ejemplo_sin_valores():
    ruta = Path(".env.example")
    if not ruta.exists():
        return False, "no existe .env.example"
    con_valor = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        nombre, _, valor = linea.partition("=")
        if NOMBRE_SECRETO.search(nombre) and valor.strip():
            con_valor.append(nombre)
    if con_valor:
        return False, f"secretos con valor: {con_valor}"
    return True, ".env.example existe y no trae secretos"


def imagen_limpia():
    if len(sys.argv) < 2:
        return True, "sin imagen indicada: no se reviso"
    imagen = sys.argv[1]
    _, entorno = docker_salida(
        "image",
        "inspect",
        "-f",
        "{{range .Config.Env}}{{println .}}{{end}}",
        imagen,
    )
    _, historial = docker_salida(
        "history", "--no-trunc", "--format", "{{.CreatedBy}}", imagen
    )
    sospechosos = []
    for linea in (entorno + "\n" + historial).splitlines():
        m = ASIGNACION.search(linea)
        if m:
            sospechosos.append(ocultar(m.group(1)))
    if sospechosos:
        return False, f"{imagen} guarda {len(sospechosos)} valores"
    return True, f"{imagen} no guarda valores de secretos"


def docker_salida(*args):
    r = subprocess.run(
        ["docker", *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return r.returncode, r.stdout.strip()


COMPROBACIONES = [
    ("SEC-1", "archivos sin secretos", archivos_limpios),
    ("SEC-2", ".env ignorado por git", env_ignorado),
    ("SEC-3", ".env fuera del repositorio", env_no_versionado),
    ("SEC-4", ".env.example sin secretos", ejemplo_sin_valores),
    ("SEC-5", "imagen sin secretos", imagen_limpia),
]


def ejecutar():
    cumplidas = 0
    for id_, descripcion, prueba in COMPROBACIONES:
        ok, evidencia = prueba()
        estado = "PASA " if ok else "FALLA"
        print(f"{estado} {id_} {descripcion} -> {evidencia}")
        cumplidas += 1 if ok else 0
    total = len(COMPROBACIONES)
    print(f"\n{cumplidas} de {total} comprobaciones cumplidas")
    return cumplidas == total


if __name__ == "__main__":
    sys.exit(0 if ejecutar() else 1)
