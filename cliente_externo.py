"""Ejecuta la tabla de casos.py contra el servicio en marcha, como lo haría un cliente externo.

Uso: python cliente_externo.py [http://127.0.0.1:8000]
"""
import sys

import httpx2

from casos import CASOS, ejecutar_caso

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    cumplidos = 0
    try:
        with httpx2.Client(base_url=base, timeout=30) as cliente:
            for caso in CASOS:
                ok, estado, cuerpo = ejecutar_caso(cliente, caso)
                print(f"{'PASA ' if ok else 'FALLA'} {caso['id']} {caso['metodo']} {caso['ruta']} -> {estado}")
                cumplidos += 1 if ok else 0
    except httpx2.ConnectError:
        sys.exit(f"No se pudo conectar a {base}. Arranca el servicio.")
    print(f"\n{cumplidos} de {len(CASOS)} casos cumplidos")
    sys.exit(0 if cumplidos == len(CASOS) else 1)
