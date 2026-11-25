"""Verifica la Matriz de Pruebas y su registro de ejecucion.

Uso:
    python verificar_matriz.py [--matriz matriz_pruebas]
Se ejecuta desde la raiz del repositorio.
"""

import re
import sys
import textwrap

from ejecutar_matriz import (
    CLASIFICACIONES,
    abrir_cliente,
    cargar,
    ejecutar,
    huella,
    registro_de,
    valor,
)

TIPOS = {"valido", "invalido", "borde"}
MINIMO = 4
CAMPOS = ("id", "tipo", "escenario", "peticion", "esperado", "cubre")
FICHA = "docs/ficha_diseno_funcional.md"
CODIGO = re.compile(r"\b(?:RF|RNF|CA)-\d{2}\b")
IMPRESCINDIBLE = re.compile(r"^Imprescindible: (.*)$", re.M)
HUELLA = re.compile(r"Huella de la matriz: ([0-9a-f]{12})")
MIN_DECISION = 20


def estructura(matriz):
    problemas, vistos = [], set()
    for e in matriz:
        falta = [c for c in CAMPOS if c not in e]
        if falta:
            problemas.append(f"{e.get('id', '?')}: faltan {falta}")
            continue
        if e["id"] in vistos:
            problemas.append(f"{e['id']}: id repetido")
        vistos.add(e["id"])
        if e["tipo"] not in TIPOS:
            problemas.append(f"{e['id']}: tipo {e['tipo']!r}")
    if len(matriz) < MINIMO:
        problemas.append(f"hay {len(matriz)}, se piden {MINIMO}")
    tipos = {e["tipo"] for e in matriz if "tipo" in e}
    if not TIPOS <= tipos:
        problemas.append(f"faltan tipos {sorted(TIPOS - tipos)}")
    if problemas:
        return False, "; ".join(problemas)
    return True, f"{len(matriz)} escenarios, los tres tipos"


def esperado_verificable(matriz):
    malos = []
    for e in matriz:
        x = e["esperado"]
        if "estado" not in x:
            malos.append(f"{e['id']}: sin estado")
        elif not (x.get("contiene") or "fuentes" in x):
            malos.append(f"{e['id']}: solo comprueba el estado")
    if malos:
        return False, "; ".join(malos)
    return True, "estado y contenido en cada esperado"


def trazabilidad(matriz):
    try:
        ficha = open(FICHA, encoding="utf-8").read()
    except OSError:
        return False, f"no existe {FICHA}"
    codigos = set(CODIGO.findall(ficha))
    usados, malos = set(), []
    for e in matriz:
        if not e["cubre"]:
            malos.append(f"{e['id']}: no cubre nada")
        for c in e["cubre"]:
            usados.add(c)
            if c not in codigos:
                malos.append(f"{e['id']}: {c} no esta en la ficha")
    exigidos = set(CODIGO.findall(IMPRESCINDIBLE.search(ficha)[1]))
    sin = sorted(exigidos - usados)
    if sin:
        malos.append(f"imprescindibles sin escenario: {sin}")
    if malos:
        return False, "; ".join(malos)
    return True, f"{len(usados)} requisitos, con los imprescindibles"


def registro_vigente(matriz, ruta):
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError:
        return False, f"no existe {ruta}"
    m = HUELLA.search(texto)
    if not m:
        return False, "el registro no trae huella"
    if m.group(1) != huella(matriz):
        return False, (
            f"huella {m.group(1)}, la matriz es {huella(matriz)}"
        )
    return True, f"registro de la matriz {m.group(1)}"


def clasificadas(resultados):
    malos = []
    for r in resultados:
        if r["resultado"] == "PASA":
            continue
        h = r["hallazgo"]
        if not h or h["clasificacion"] not in CLASIFICACIONES:
            malos.append(f"{r['id']}: falla sin clasificar")
        elif h["clasificacion"] != "limitacion":
            malos.append(f"{r['id']}: {h['clasificacion']} abierta")
        elif len(h["decision"]) < MIN_DECISION:
            malos.append(f"{r['id']}: decision demasiado corta")
    if malos:
        return False, "; ".join(malos)
    n = sum(r["resultado"] == "FALLA" for r in resultados)
    if n == 0:
        return True, "ninguna falla"
    return True, f"{n} limitacion(es) declarada(s)"


def sin_errores_5xx(resultados):
    malos = [r["id"] for r in resultados if r["estado"] >= 500]
    if malos:
        return False, f"respuestas 5xx en {malos}"
    return True, "ningun escenario provoca un 5xx"


def main(argumentos):
    nombre = valor(argumentos, "--matriz", "matriz_pruebas")
    matriz = cargar(nombre)
    resultados = ejecutar(abrir_cliente(), matriz)
    comprobaciones = [
        ("MAT-1", "estructura", estructura(matriz)),
        ("MAT-2", "esperado claro", esperado_verificable(matriz)),
        ("MAT-3", "trazabilidad", trazabilidad(matriz)),
        (
            "MAT-4",
            "registro vigente",
            registro_vigente(matriz, registro_de(nombre)),
        ),
        ("MAT-5", "fallas clasificadas", clasificadas(resultados)),
        ("MAT-6", "sin errores 5xx", sin_errores_5xx(resultados)),
    ]
    cumplidas = 0
    for id_, nombre_, (ok, evidencia) in comprobaciones:
        cumplidas += ok
        marca = "PASA " if ok else "FALLA"
        linea = f"{marca} {id_} {nombre_} -> {evidencia}"
        print(textwrap.fill(linea, 70, subsequent_indent="      "))
    total = len(comprobaciones)
    print(f"\n{cumplidas} de {total} comprobaciones cumplidas")
    return 0 if cumplidas == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
