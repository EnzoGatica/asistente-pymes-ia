"""Verifica la matriz de riesgos y ejecuta la evidencia de cada una.

Uso:
    python verificar_riesgos.py
Se ejecuta desde la raiz del repositorio.
"""

import re
import subprocess
import sys
import textwrap

from fastapi.testclient import TestClient

import riesgos
from alucinaciones import SONDAS
from ataques import ATAQUES
from ejecutar_matriz import cargar, ejecutar
from servicio.main import app
from verificar_mitigaciones import (
    FUGAS,
    contener_alucinaciones,
    correr_ataque,
)

CAMPOS = (
    "id", "riesgo", "probabilidad", "impacto", "mitigacion",
    "evidencia", "estado", "residual",
)
MINIMO = 6
MIN_NOTA = 20
HUELLA = re.compile(r"Huella de la matriz: ([0-9a-f]{12})")


def estructura(lista):
    problemas, vistos = [], set()
    for r in lista:
        falta = [c for c in CAMPOS if c not in r]
        if falta:
            problemas.append(f"{r.get('id', '?')}: faltan {falta}")
            continue
        if r["id"] in vistos:
            problemas.append(f"{r['id']}: id repetido")
        vistos.add(r["id"])
        valores = [r["probabilidad"], r["impacto"],
                   *r["residual"].values()]
        if not all(isinstance(v, int) and 1 <= v <= 5
                   for v in valores):
            problemas.append(f"{r['id']}: valores fuera de 1 a 5")
        if r["estado"] not in riesgos.ESTADOS:
            problemas.append(f"{r['id']}: estado {r['estado']!r}")
        if not r["evidencia"]:
            problemas.append(f"{r['id']}: sin evidencia")
    if len(lista) < MINIMO:
        problemas.append(f"hay {len(lista)}, se piden {MINIMO}")
    if problemas:
        return False, "; ".join(problemas)
    return True, f"{len(lista)} riesgos completos"


def residual_coherente(lista):
    malos = []
    for r in lista:
        antes, despues = riesgos.inherente(r), riesgos.residual(r)
        if despues > antes:
            malos.append(f"{r['id']}: residual {despues} > {antes}")
        elif r["estado"] != "aceptada" and despues == antes:
            malos.append(f"{r['id']}: mitiga y no baja el riesgo")
        elif r["estado"] == "aceptada" and despues != antes:
            malos.append(f"{r['id']}: acepta pero cambia el riesgo")
    if malos:
        return False, "; ".join(malos)
    return True, "ninguna mitigacion sube ni deja igual el riesgo"


def resolver(ref, cliente):
    """Ejecuta una evidencia: PASA, LIMITE, FALLA o DESCONOCIDA."""
    tipo, _, nombre = ref.partition(":")
    if tipo == "ataques":
        ataque = next((a for a in ATAQUES if a["id"] == nombre), None)
        if ataque is None:
            return "DESCONOCIDA"
        return correr_ataque(cliente, ataque)["resultado"]
    if tipo == "fuga":
        funcion = {i: f for i, _, f in FUGAS}.get(nombre)
        if funcion is None:
            return "DESCONOCIDA"
        return "PASA" if funcion(cliente)[0] else "FALLA"
    if tipo == "alucinacion":
        filas = {f[1]: f[0] for f in contener_alucinaciones(cliente)}
        return filas.get(nombre, "DESCONOCIDA")
    if tipo in ("matriz", "matriz_modelo"):
        modulo = "matriz_pruebas" if tipo == "matriz" else tipo
        matriz = [e for e in cargar(modulo) if e["id"] == nombre]
        if not matriz:
            return "DESCONOCIDA"
        r = ejecutar(cliente, matriz)[0]
        if r["resultado"] == "PASA":
            return "PASA"
        declarada = (r["hallazgo"] or {}).get("clasificacion")
        return "LIMITE" if declarada == "limitacion" else "FALLA"
    if tipo in ("pruebas", "comando"):
        orden = (
            [sys.executable, "-m", "pytest", "-q", nombre]
            if tipo == "pruebas"
            else nombre.replace("python", sys.executable, 1).split()
        )
        hecho = subprocess.run(orden, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return "PASA" if hecho.returncode == 0 else "FALLA"
    return "DESCONOCIDA"


def evidencia_ejecutada(lista, cliente):
    malos = []
    for r in lista:
        for ref in r["evidencia"]:
            veredicto = resolver(ref, cliente)
            if r["estado"] == "aceptada":
                bueno = veredicto == "LIMITE"
            else:
                bueno = veredicto == "PASA"
            if not bueno:
                malos.append(f"{r['id']}: {ref} -> {veredicto}")
    if malos:
        return False, "; ".join(malos)
    total = sum(len(r["evidencia"]) for r in lista)
    return True, f"{total} evidencias, todas como se declaro"


def limites_declarados(lista):
    malos = []
    cubiertos = {x for r in lista for x in r.get("limites", [])}
    en_codigo = {a["id"] for a in ATAQUES if "hallazgo" in a}
    en_codigo |= {s["id"] for s in SONDAS if "decision" in s}
    try:  # matriz_modelo es opcional: este proyecto no la usa
        en_codigo |= {
            e["id"]
            for e in cargar("matriz_modelo")
            if e.get("hallazgo", {}).get("clasificacion") == "limitacion"
        }
    except ModuleNotFoundError:
        pass
    for r in lista:
        if r["estado"] in ("parcial", "aceptada"):
            nota = r.get("nota", "")
            if len(nota) < MIN_NOTA or not r.get("limites"):
                malos.append(f"{r['id']}: sin nota o sin limites")
    sin_riesgo = sorted(en_codigo - cubiertos)
    if sin_riesgo:
        malos.append(f"limitaciones sin riesgo: {sin_riesgo}")
    if malos:
        return False, "; ".join(malos)
    return True, f"{len(en_codigo)} limitaciones, cada una cubierta"


def supervision(lista):
    malos = []
    for r in lista:
        nivel = riesgos.categoria(riesgos.residual(r))
        if nivel in ("ALTO", "CRITICO") and not r.get("supervision"):
            malos.append(f"{r['id']}: {nivel} sin supervision")
    if malos:
        return False, "; ".join(malos)
    return True, "los riesgos altos que quedan tienen supervision"


def registro_vigente():
    try:
        texto = riesgos.REGISTRO.read_text(encoding="utf-8")
    except OSError:
        return False, f"no existe {riesgos.REGISTRO}"
    m = HUELLA.search(texto)
    if not m:
        return False, "el registro no trae huella"
    if m.group(1) != riesgos.huella():
        actual = riesgos.huella()
        return False, f"huella {m.group(1)}, la matriz es {actual}"
    return True, f"registro de la matriz {m.group(1)}"


def main():
    lista = riesgos.RIESGOS
    cliente = TestClient(app, raise_server_exceptions=False)
    comprobaciones = [
        ("RIE-1", "estructura", estructura(lista)),
        ("RIE-2", "residual coherente", residual_coherente(lista)),
        ("RIE-3", "evidencia", evidencia_ejecutada(lista, cliente)),
        ("RIE-4", "limitaciones", limites_declarados(lista)),
        ("RIE-5", "supervision", supervision(lista)),
        ("RIE-6", "registro vigente", registro_vigente()),
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
