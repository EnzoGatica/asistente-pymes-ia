"""Ejecuta ataques, sondas de alucinación y pruebas de fuga contra la API en memoria, sin OpenAI.

Uso:
    python verificar_mitigaciones.py
Resultado por fila: PASA (contenido), LIMITE (no contenido, aceptado con decisión) o FALLA.
"""
import os
import sys

from fastapi.testclient import TestClient

from alucinaciones import SONDAS
from ataques import ATAQUES
from dobles import motor_simulado
from servicio.main import app
from servicio_rag import SIN_CONTEXTO
from src.logging_rag import CARPETA_LOGS

RESPUESTA_NORMAL = "Despachamos a Dichato por $3.500 [despacho.md]."
LOG = CARPETA_LOGS / "servicio_rag.log"


def correr_ataque(cliente, ataque):
    with motor_simulado(RESPUESTA_NORMAL, ataque.get("fragmentos_extra")):
        r = cliente.post("/consultas", json={"pregunta": ataque["pregunta"]})
    esperado, motivos = ataque["esperado"], []
    if r.status_code != esperado["estado"]:
        motivos.append(f"estado {r.status_code}")
    if "fuente_ausente" in esperado and esperado["fuente_ausente"] in r.text:
        motivos.append(f"usa {esperado['fuente_ausente']}")
    if not motivos:
        resultado = "PASA"
    else:
        resultado = "LIMITE" if "hallazgo" in ataque else "FALLA"
    return {"id": ataque["id"], "resultado": resultado, "motivos": motivos}


def contener_alucinaciones(cliente):
    filas = []
    for sonda in SONDAS:
        with motor_simulado(sonda["respuesta"]):
            r = cliente.post("/consultas", json={"pregunta": sonda["pregunta"]})
        contenida = SIN_CONTEXTO in r.text and r.json().get("fuentes") == []
        nombre = f"alucinacion: {sonda['tipo']}"
        if contenida:
            filas.append(("PASA", sonda["id"], nombre, ""))
        elif "decision" in sonda:
            filas.append(("LIMITE", sonda["id"], nombre, sonda["decision"]))
        else:
            filas.append(("FALLA", sonda["id"], nombre, "llega al usuario"))
    return filas


def fuga_en_registros(cliente):
    marca = "marcador-privado-7f3a"
    antes = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    with motor_simulado(RESPUESTA_NORMAL):
        cliente.post("/consultas", json={"pregunta": f"¿Despachan a Dichato? {marca}"})
    nuevo = (LOG.read_text(encoding="utf-8") if LOG.exists() else "")[len(antes):]
    return marca not in nuevo and bool(nuevo), "la pregunta no aparece en logs/servicio_rag.log"


def fuga_de_clave(cliente):
    clave = os.environ.get("OPENAI_API_KEY") or "sin-clave-definida"
    textos = [cliente.get("/salud").text, cliente.post("/consultas", json={"pregunta": ""}).text]
    return all(clave not in t for t in textos), "la clave no aparece en /salud ni en errores"


def fuga_en_errores(cliente):
    marca = "valor-enviado-9c1e" * 40
    r = cliente.post("/consultas", json={"pregunta": marca})
    return r.status_code == 422 and "valor-enviado" not in r.text, "el error nombra el campo, no su valor"


FUGAS = [
    ("F-01", "texto de la pregunta en los registros", fuga_en_registros),
    ("F-02", "clave del modelo en respuestas", fuga_de_clave),
    ("F-03", "errores que repiten lo enviado", fuga_en_errores),
]


def main():
    cliente = TestClient(app, raise_server_exceptions=False)
    filas = []
    for ataque in ATAQUES:
        r = correr_ataque(cliente, ataque)
        filas.append((r["resultado"], r["id"], ataque["tipo"], ataque.get("hallazgo", "; ".join(r["motivos"]))))
    filas += contener_alucinaciones(cliente)
    for id_, nombre, prueba in FUGAS:
        ok, evidencia = prueba(cliente)
        filas.append(("PASA" if ok else "FALLA", id_, nombre, evidencia))
    for resultado, id_, nombre, detalle in filas:
        print(f"{resultado:6} {id_} {nombre}" + (f" -> {detalle[:90]}" if detalle else ""))
    fallan = [f for f in filas if f[0] == "FALLA"]
    limites = [f for f in filas if f[0] == "LIMITE"]
    print(f"\n{len(filas) - len(fallan)} de {len(filas)} comprobaciones cumplidas, "
          f"{len(limites)} limitacion(es) declarada(s)")
    return 0 if not fallan else 1


if __name__ == "__main__":
    sys.exit(main())
