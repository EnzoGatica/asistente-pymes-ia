"""Verifica que el entorno está listo para correr el servicio del Gate 2. Nunca imprime la clave."""
import os
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PAQUETES = ["langchain-core", "langchain-openai", "langchain-chroma", "langgraph", "python-dotenv", "pytest"]
VARIABLES = ["OPENAI_API_KEY"]
INDICE_DIR = Path(__file__).resolve().parent / "vectorstore"

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

problemas = []
print("Python:", sys.version.split()[0])
if sys.version_info < (3, 10):
    problemas.append("usar Python 3.10 o superior")

for paquete in PAQUETES:
    try:
        print(f"{paquete}: {version(paquete)}")
    except PackageNotFoundError:
        print(f"{paquete}: NO instalado")
        problemas.append(f"instalar {paquete}")

for nombre in VARIABLES:
    valor = os.getenv(nombre, "")
    estado = "definida" if valor and valor != "tu_llave_aqui" else "FALTA"
    print(f"{nombre}: {estado}")
    if estado == "FALTA":
        problemas.append(f"definir {nombre} en el archivo .env")

if INDICE_DIR.is_dir() and any(INDICE_DIR.iterdir()):
    print("indice en vectorstore/: ok")
else:
    print("indice en vectorstore/: no existe todavía (servicio_rag.py lo crea en la primera consulta)")

print()
if problemas:
    print("Pendiente: " + "; ".join(problemas))
    sys.exit(1)
print("Entorno listo para la corrida final")
