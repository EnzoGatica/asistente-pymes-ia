import os
import subprocess
import sys
import time

import httpx2

from casos import CASOS, ejecutar_caso

IMAGEN = sys.argv[1] if len(sys.argv) > 1 else "asistente-espiga:0.3"
NOMBRE = "verificacion-imagen"
PUERTO = 8099
BASE = f"http://127.0.0.1:{PUERTO}"


def docker(*args):
    r = subprocess.run(
        ["docker", *args], capture_output=True, text=True
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def arrancar():
    publicar = f"{PUERTO}:8000"
    # la clave entra al ejecutar, nunca queda en la imagen; sin .env las consultas responden 503
    clave = ["--env-file", ".env"] if os.path.exists(".env") else []
    docker("run", "-d", "--name", NOMBRE, "-p", publicar, *clave, IMAGEN)


def esperar(url, segundos=20):
    limite = time.time() + segundos
    while time.time() < limite:
        try:
            if httpx2.get(url, timeout=2).status_code == 200:
                return True
        except httpx2.HTTPError:
            pass
        time.sleep(0.5)
    return False


def existe_imagen():
    codigo, _ = docker("image", "inspect", IMAGEN)
    if codigo != 0:
        return False, f"no existe la imagen {IMAGEN}"
    return True, f"imagen {IMAGEN}"


def responde_salud():
    esperado = esperar(BASE + "/salud")
    return esperado, f"GET /salud en el puerto {PUERTO}"


def usuario_comun():
    _, uid = docker("exec", NOMBRE, "id", "-u")
    return uid != "0", f"uid del proceso: {uid}"


def sin_claves():
    _, listado = docker("exec", NOMBRE, "ls", "-a", "/app")
    archivos = listado.split()
    ok = ".env" not in archivos and ".git" not in archivos
    return ok, f"contenido de /app: {archivos}"


def casos_pasan():
    with httpx2.Client(base_url=BASE, timeout=30) as cliente:
        resultados = [ejecutar_caso(cliente, c) for c in CASOS]
    bien = sum(1 for ok, _, _ in resultados if ok)
    return bien == len(CASOS), f"{bien} de {len(CASOS)} casos"


def con_salud():
    plantilla = (
        "{{if .State.Health}}{{.State.Health.Status}}"
        "{{else}}sin healthcheck{{end}}"
    )
    for _ in range(20):
        _, estado = docker("inspect", "-f", plantilla, NOMBRE)
        if estado in ("healthy", "sin healthcheck"):
            break
        time.sleep(1)
    return estado == "healthy", f"estado de salud: {estado}"


COMPROBACIONES = [
    ("IMG-1", "la imagen existe", existe_imagen),
    ("IMG-2", "el contenedor responde en /salud", responde_salud),
    ("IMG-3", "no corre como administrador", usuario_comun),
    ("IMG-4", "sin claves ni git dentro", sin_claves),
    ("IMG-5", "la tabla de casos pasa", casos_pasan),
    ("IMG-6", "el contenedor se declara sano", con_salud),
]


def ejecutar():
    cumplidas = 0
    try:
        docker("rm", "-f", NOMBRE)
        for i, (id_, descripcion, prueba) in enumerate(COMPROBACIONES):
            if i == 1:
                arrancar()
            try:
                ok, evidencia = prueba()
            except Exception as error:
                ok, evidencia = False, f"error: {error!r}"
            estado = "PASA " if ok else "FALLA"
            print(f"{estado} {id_} {descripcion} -> {evidencia}")
            cumplidas += 1 if ok else 0
            if i == 0 and not ok:
                break
    finally:
        docker("rm", "-f", NOMBRE)
    total = len(COMPROBACIONES)
    print(f"\n{cumplidas} de {total} comprobaciones cumplidas")
    return cumplidas == total


if __name__ == "__main__":
    sys.exit(0 if ejecutar() else 1)
