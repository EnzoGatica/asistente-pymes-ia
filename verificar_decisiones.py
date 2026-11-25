"""Verifica las decisiones y las limitaciones documentadas.

Uso:
    python verificar_decisiones.py
Se ejecuta desde la raiz del repositorio.
"""

import re
import sys
import textwrap
from pathlib import Path

import riesgos
import transferencia
from alucinaciones import SONDAS
from ataques import ATAQUES
from ejecutar_matriz import cargar

DECISIONES = Path("docs/decisiones.md")
LIMITACIONES = Path("docs/limitaciones.md")
README = Path("README.md")
CAMPOS = ("Estado", "Contexto", "Decisión",
          "Alternativas descartadas", "Costo")
MINIMO_DECISIONES = 5
MIN_TEXTO = 30
ID_D = re.compile(r"\bD-\d{2}\b")
ID_L = re.compile(r"LIM-\d{2}")


def leer_decisiones():
    """Devuelve {id: {campo: texto}} de docs/decisiones.md."""
    texto = DECISIONES.read_text(encoding="utf-8")
    resultado = {}
    partes = re.split(r"^## (D-\d{2}) .*$", texto, flags=re.M)
    for i in range(1, len(partes), 2):
        campos, actual = {}, None
        for linea in partes[i + 1].splitlines():
            m = re.match(r"- \*\*(.+?):\*\* ?(.*)", linea)
            if m:
                actual = m.group(1)
                campos[actual] = m.group(2)
            elif actual and linea.startswith("  "):
                campos[actual] += " " + linea.strip()
        resultado[partes[i]] = campos
    return resultado


def leer_limitaciones():
    """Devuelve {id: {columna: texto}} de la tabla."""
    filas = {}
    texto = LIMITACIONES.read_text(encoding="utf-8")
    for linea in texto.splitlines():
        crudas = linea.strip().strip("|").split("|")
        celdas = [c.strip() for c in crudas]
        if len(celdas) == 6 and ID_L.fullmatch(celdas[0]):
            filas[celdas[0]] = {
                "que": celdas[1], "origen": celdas[2],
                "riesgo": celdas[3], "efecto": celdas[4],
                "decision": celdas[5],
            }
    return filas


def declaradas():
    """Limitaciones que el proyecto declara en su propio codigo."""
    origenes = {f"ataques:{a['id']}" for a in ATAQUES
                if a.get("hallazgo", {}).get("clasificacion")
                == "limitacion"}
    origenes |= {f"alucinaciones:{s['id']}" for s in SONDAS
                 if "decision" in s}
    for nombre in ("matriz_modelo", "matriz_pruebas"):
        try:  # matriz_modelo es opcional: este proyecto no la usa
            matriz = cargar(nombre)
        except ModuleNotFoundError:
            continue
        origenes |= {
            f"{nombre}:{e['id']}" for e in matriz
            if e.get("hallazgo", {}).get("clasificacion")
            == "limitacion"
        }
    observaciones = transferencia.OBSERVACIONES
    origenes |= {
        f"transferencia:{o['id']}" for o in observaciones
        if o["causa"] == "producto"
    }
    return origenes


def decisiones_completas(decisiones):
    malos = []
    if len(decisiones) < MINIMO_DECISIONES:
        malos.append(f"hay {len(decisiones)}, se piden "
                     f"{MINIMO_DECISIONES}")
    for id_, campos in decisiones.items():
        faltan = [c for c in CAMPOS if not campos.get(c)]
        if faltan:
            malos.append(f"{id_}: faltan {faltan}")
        elif campos["Estado"] not in ("vigente", "reemplazada"):
            malos.append(f"{id_}: estado {campos['Estado']!r}")
    if malos:
        return False, "; ".join(malos)
    return True, f"{len(decisiones)} decisiones con sus cinco campos"


def costos_reales(decisiones):
    malos = []
    for id_, campos in decisiones.items():
        for campo in ("Alternativas descartadas", "Costo"):
            if len(campos.get(campo, "")) < MIN_TEXTO:
                malos.append(f"{id_}: {campo} demasiado corto")
    if malos:
        return False, "; ".join(malos)
    return True, "cada decision dice que descarto y que cuesta"


def readme_cita(decisiones):
    texto = README.read_text(encoding="utf-8")
    malos = []
    citadas = set(ID_D.findall(texto))
    for id_, campos in decisiones.items():
        if campos.get("Estado") == "vigente" and id_ not in citadas:
            malos.append(f"el README no cita {id_}")
    for id_ in sorted(citadas - set(decisiones)):
        malos.append(f"el README cita {id_} y no existe")
    for ruta in ("docs/decisiones.md", "docs/limitaciones.md"):
        if ruta not in texto:
            malos.append(f"el README no enlaza {ruta}")
    if malos:
        return False, "; ".join(malos)
    return True, (f"el README cita {len(citadas)} decisiones y "
                  "enlaza los dos documentos")


def limitaciones_completas(filas):
    registradas = set()
    for fila in filas.values():
        registradas |= {o.strip() for o in fila["origen"].split(",")}
    en_codigo = declaradas()
    malos = []
    for origen in sorted(en_codigo - registradas):
        malos.append(f"{origen} se declara y no esta registrada")
    for origen in sorted(registradas - en_codigo):
        malos.append(f"{origen} esta registrada y no se declara")
    if malos:
        return False, "; ".join(malos)
    return True, (f"{len(en_codigo)} origenes declarados, todos "
                  f"en {len(filas)} limitaciones")


def limitaciones_utiles(filas):
    ids_riesgo = {r["id"]: r for r in riesgos.RIESGOS}
    malos = []
    for id_, f in filas.items():
        for campo in ("efecto", "decision"):
            if len(f[campo]) < MIN_TEXTO:
                malos.append(f"{id_}: {campo} demasiado corto")
        r = ids_riesgo.get(f["riesgo"])
        if r is None:
            malos.append(f"{id_}: el riesgo {f['riesgo']} no existe")
            continue
        if r["estado"] not in ("parcial", "aceptada"):
            malos.append(f"{id_}: {f['riesgo']} esta {r['estado']}")
        for origen in f["origen"].split(","):
            corto = origen.split(":")[1].strip()
            if corto not in r.get("limites", []):
                malos.append(f"{id_}: {r['id']} no lista {corto}")
    if malos:
        return False, "; ".join(malos)
    return True, "cada limitacion dice efecto, decision y riesgo"


def readme_limitaciones(filas):
    texto = README.read_text(encoding="utf-8")
    faltan = [i for i in filas if i not in texto]
    if faltan:
        return False, "el README no menciona " + ", ".join(faltan)
    return True, f"el README menciona las {len(filas)} limitaciones"


def transferencia_registrada(filas):
    malos = []
    for o in transferencia.OBSERVACIONES:
        if o["causa"] != "producto":
            continue
        fila = filas.get(o["ref"])
        if fila is None:
            malos.append(f"{o['id']}: {o['ref']} no existe")
        elif f"transferencia:{o['id']}" not in fila["origen"]:
            malos.append(f"{o['ref']} no cita {o['id']}")
    if malos:
        return False, "; ".join(malos)
    return True, "lo que hallo la prueba esta en limitaciones.md"


def main():
    decisiones = leer_decisiones()
    filas = leer_limitaciones()
    comprobaciones = [
        ("DEC-1", "decisiones", decisiones_completas(decisiones)),
        ("DEC-2", "costos reales", costos_reales(decisiones)),
        ("DEC-3", "README cita", readme_cita(decisiones)),
        ("DEC-4", "limitaciones", limitaciones_completas(filas)),
        ("DEC-5", "limitaciones utiles", limitaciones_utiles(filas)),
        ("DEC-6", "README las lista", readme_limitaciones(filas)),
        ("DEC-7", "transferencia", transferencia_registrada(filas)),
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
