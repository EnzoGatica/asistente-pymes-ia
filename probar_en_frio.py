"""Sigue el README al pie de la letra sobre un clon limpio.

Uso:
    python probar_en_frio.py
Se ejecuta desde la raiz del repositorio, con todo guardado en git:
solo lo que esta en un commit llega al clon.
"""

import json
import shutil
import os
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.request
from pathlib import Path

from verificar_readme import README, cuerpo_de

WINDOWS = os.name == "nt"
PUERTO = 8000
PREGUNTA = "¿Despachan a Dichato?"


def lineas_de_codigo(texto, clave, contiene=None):
    """Lineas del primer bloque de la seccion `clave`."""
    cuerpo = cuerpo_de(texto, clave)
    for bloque in cuerpo.split("```")[1::2]:
        lineas = [l.strip() for l in bloque.splitlines()[1:]]
        lineas = [l for l in lineas if l and not l.startswith("#")]
        if contiene is None or any(contiene in l for l in lineas):
            return lineas
    return []


def ejecutar(orden, carpeta, entorno):
    r = subprocess.run(
        orden, shell=True, cwd=carpeta, env=entorno,
        capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    texto = r.stdout + r.stderr
    salida = [l for l in texto.splitlines() if l.strip()]
    return r.returncode, (salida[-1][:110] if salida else "")


def carpeta_scripts(venv):
    """Donde el entorno virtual deja pip y uvicorn."""
    return venv / ("Scripts" if WINDOWS else "bin")


def detener(proceso):
    """Cierra el servicio y todo lo que arranco para dejarlo en marcha."""
    if WINDOWS:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proceso.pid)],
            capture_output=True,
        )
    else:
        proceso.terminate()
    proceso.wait()


def puerto_libre():
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", PUERTO)) != 0


def pedir(ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo else None
    peticion = urllib.request.Request(
        f"http://127.0.0.1:{PUERTO}{ruta}", data=datos,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(peticion, timeout=30) as r:  # la primera consulta indexa corpus/
        return json.load(r)


def esperar_salud():
    for _ in range(40):
        try:
            return pedir("/salud")
        except OSError:
            time.sleep(0.5)
    return None


def paso(resultados, id_, nombre, ok, evidencia):
    resultados.append((id_, nombre, ok, evidencia))
    marca = "PASA " if ok else "FALLA"
    linea = f"{marca} {id_} {nombre} -> {evidencia}"
    print(textwrap.fill(linea, 70, subsequent_indent="      "))
    return ok


def recorrido(resultados):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        clon = Path(tmp) / "proyecto"
        r = subprocess.run(
            ["git", "clone", "--quiet", ".", str(clon)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        archivos = subprocess.run(
            ["git", "ls-files"], cwd=clon, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        ).stdout.split()
        if not paso(resultados, "FRIO-1", "clon limpio",
                    r.returncode == 0 and bool(archivos),
                    f"{len(archivos)} archivos llegan desde git"):
            return
        if Path(".env").exists():  # el paso Configuracion del README: cp .env.example .env y completar la llave
            shutil.copy(".env", clon / ".env")
        texto = (clon / README).read_text(encoding="utf-8")
        entorno = dict(os.environ)
        scripts = carpeta_scripts(clon / ".venv")
        entorno["PATH"] = f"{scripts}{os.pathsep}" + entorno["PATH"]
        entorno.pop("PYTHONPATH", None)
        entorno.pop("VIRTUAL_ENV", None)
        entorno["PYTHONUTF8"] = "1"
        pasos = [
            l for l in lineas_de_codigo(texto, "instalacion")
            if not l.startswith(("source", ".venv\\"))
        ]
        if not pasos:
            paso(resultados, "FRIO-2", "instalacion", False,
                 "el README no trae comandos de instalacion")
            return
        for orden in pasos:
            codigo, ultima = ejecutar(orden, clon, entorno)
            if codigo != 0:
                paso(resultados, "FRIO-2", "instalacion", False,
                     f"{orden!r} termina con {codigo}: {ultima}")
                return
        paso(resultados, "FRIO-2", "instalacion", True,
             f"{len(pasos)} comandos del README terminaron bien")
        prueba = "python -m pytest -q"
        codigo, ultima = ejecutar(prueba, clon, entorno)
        paso(resultados, "FRIO-3", "pruebas", codigo == 0, ultima)
        arranque = lineas_de_codigo(texto, "arrancar", "uvicorn")
        if not arranque:
            paso(resultados, "FRIO-4", "arranque", False,
                 "el README no dice como arrancar sin Docker")
            return
        if not puerto_libre():
            paso(resultados, "FRIO-4", "arranque", False,
                 f"el puerto {PUERTO} esta ocupado; detiene lo que "
                 "lo usa")
            return
        orden = arranque[0] if WINDOWS else "exec " + arranque[0]
        servidor = subprocess.Popen(
            orden, shell=True, cwd=clon, env=entorno,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            salud = esperar_salud()
            paso(resultados, "FRIO-4", "arranque", salud is not None,
                 f"/salud responde {salud}" if salud else
                 "el servicio no respondio en 20 segundos")
            if salud:
                r = pedir("/consultas", {"pregunta": PREGUNTA})
                ok = "despacho.md" in r.get("fuentes", [])
                paso(resultados, "FRIO-5", "consulta", ok,
                     f"fuentes: {r.get('fuentes')}")
        finally:
            detener(servidor)


def main():
    resultados = []
    recorrido(resultados)
    cumplidas = sum(ok for _, _, ok, _ in resultados)
    print(f"\n{cumplidas} de {len(resultados)} pasos cumplidos")
    return 0 if all(ok for _, _, ok, _ in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
