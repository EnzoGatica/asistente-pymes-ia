"""Introduce un defecto en una copia y comprueba si una prueba lo ve.

Uso:
    python verificar_defectos.py ARCHIVO "TEXTO_ACTUAL" "TEXTO_NUEVO" PRUEBA
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IGNORAR = shutil.ignore_patterns(
    "__pycache__", ".pytest_cache", ".git", ".venv", "venv", "vectorstore", "logs"
)


def main(archivo, viejo, nuevo, prueba):
    origen = Path(archivo)
    if not origen.exists() or not Path(prueba).exists():
        print("ERROR no existe el archivo o la prueba indicada")
        return 2
    veces = origen.read_text(encoding="utf-8").count(viejo)
    if veces != 1:
        print(f"ERROR el texto aparece {veces} veces en {archivo}; ")
        print("      usa un fragmento que aparezca exactamente una vez")
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "copia"
        shutil.copytree(".", copia, ignore=IGNORAR)
        destino = copia / archivo
        texto = destino.read_text(encoding="utf-8")
        destino.write_text(
            texto.replace(viejo, nuevo), encoding="utf-8"
        )
        r = subprocess.run(
            [sys.executable, "-m", "pytest", prueba, "-q", "--tb=no"],
            cwd=copia,
            capture_output=True,
            text=True,
        )
    fallan = re.findall(r"^FAILED (\S+)", r.stdout, re.MULTILINE)
    print(f"defecto en {archivo}: {viejo!r} -> {nuevo!r}")
    if fallan:
        print(f"DETECTADO: fallan {len(fallan)} prueba(s) de {prueba}")
        for nombre in fallan:
            print("  ", nombre.split("::")[-1])
        return 0
    print(f"NO DETECTADO: todas las pruebas de {prueba} siguen pasando")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
