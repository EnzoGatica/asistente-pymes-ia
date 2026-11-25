"""Matriz de riesgos del asistente de la Panaderia La Espiga, con mitigaciones verificadas.

Cada riesgo trae su mitigacion, la evidencia que se puede ejecutar
para comprobarla y el riesgo que queda despues de mitigar.

Uso:
    python riesgos.py [--escribir]
"""

import hashlib
import json
import sys
import textwrap
from datetime import date
from pathlib import Path

REGISTRO = Path("docs/matriz_riesgos.md")
ESTADOS = ("verificada", "parcial", "aceptada")


def puntaje(probabilidad, impacto):
    return probabilidad * impacto


def categoria(valor):
    if valor >= 15:
        return "CRITICO"
    if valor >= 9:
        return "ALTO"
    if valor >= 4:
        return "MEDIO"
    return "BAJO"


RIESGOS = [
    {
        "id": "R-01",
        "riesgo": "Orden escondida en un fragmento de corpus/ (inyeccion indirecta)",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": "Filtro de patrones sobre los fragmentos recuperados y prompt que trata el contexto como datos",
        "evidencia": ["ataques:A-01", "pruebas:tests/parciales/test_inyeccion.py"],
        "estado": "parcial",
        "residual": {"probabilidad": 3, "impacto": 4},
        "limites": ["A-03"],
        "nota": "Una orden redactada con otras palabras pasa el filtro de patrones (A-03)",
        "supervision": "La duena revisa cada respuesta antes de enviarla y se amplian los patrones con cada caso nuevo",
    },
    {
        "id": "R-02",
        "riesgo": "Respuesta con un dato que corpus/ no respalda",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": "Prompt que exige usar solo el contexto y deteccion de sin informacion con fuentes vacias",
        "evidencia": ["alucinacion:H-01", "alucinacion:H-02", "pruebas:tests/parciales/test_sin_cobertura.py"],
        "estado": "parcial",
        "residual": {"probabilidad": 3, "impacto": 4},
        "limites": ["H-03"],
        "nota": "Un precio inventado con cita no se detecta: no se comparan cifras con el contexto (H-03)",
        "supervision": "La duena revisa cada respuesta antes de enviarla; precios y plazos se confirman contra corpus/",
    },
    {
        "id": "R-03",
        "riesgo": "Fuga de la clave de OpenAI",
        "probabilidad": 2,
        "impacto": 5,
        "mitigacion": "Clave solo en variables de entorno, nunca en la imagen, compose.yaml ni git",
        "evidencia": ["fuga:F-02", "comando:python buscar_secretos.py"],
        "estado": "verificada",
        "residual": {"probabilidad": 1, "impacto": 5},
    },
    {
        "id": "R-04",
        "riesgo": "Datos personales de clientes en los registros",
        "probabilidad": 3,
        "impacto": 5,
        "mitigacion": "Se registran longitud y huella de la pregunta, nunca su texto",
        "evidencia": ["fuga:F-01", "pruebas:tests/test_gate2.py"],
        "estado": "verificada",
        "residual": {"probabilidad": 1, "impacto": 5},
    },
    {
        "id": "R-05",
        "riesgo": "Los errores repiten lo que envio el cliente",
        "probabilidad": 2,
        "impacto": 3,
        "mitigacion": "Errores uniformes con codigo y mensaje que nombran el campo, no su valor",
        "evidencia": ["fuga:F-03"],
        "estado": "verificada",
        "residual": {"probabilidad": 1, "impacto": 3},
    },
    {
        "id": "R-06",
        "riesgo": "Entradas malformadas o gigantes tumban el servicio",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": "Validacion con pydantic (3 a 500 caracteres, espacios recortados) antes de llamar al modelo",
        "evidencia": ["ataques:A-02", "matriz:MP-02", "matriz:MP-03", "matriz:MP-05"],
        "estado": "verificada",
        "residual": {"probabilidad": 1, "impacto": 3},
    },
    {
        "id": "R-07",
        "riesgo": "El filtro bloquea preguntas legitimas",
        "probabilidad": 2,
        "impacto": 2,
        "mitigacion": "El filtro actua sobre los fragmentos recuperados, no sobre la pregunta del cliente",
        "evidencia": ["ataques:B-01", "ataques:B-02"],
        "estado": "verificada",
        "residual": {"probabilidad": 1, "impacto": 2},
    },
    {
        "id": "R-08",
        "riesgo": "El proveedor da de baja el modelo o deja de responder",
        "probabilidad": 3,
        "impacto": 4,
        "mitigacion": "Modelo de respaldo en una sola constante y respuesta 503 controlada, sin detalles internos",
        "evidencia": ["pruebas:tests/test_api.py::test_proveedor_caido_responde_503_sin_detalles"],
        "estado": "verificada",
        "residual": {"probabilidad": 2, "impacto": 3},
    },
]

def inherente(r):
    return puntaje(r["probabilidad"], r["impacto"])


def residual(r):
    d = r["residual"]
    return puntaje(d["probabilidad"], d["impacto"])


def huella():
    texto = json.dumps(RIESGOS, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(texto.encode()).hexdigest()[:12]


def cifra(valor):
    return f"{valor} {categoria(valor)}"


def escribir_registro():
    lineas = [
        "# Matriz de riesgos",
        "",
        f"Fecha: {date.today().isoformat()}",
        f"Huella de la matriz: {huella()}",
        f"Riesgos: {len(RIESGOS)}",
        "",
        "| ID | Riesgo | Inherente | Mitigacion | Evidencia | Estado | Residual | Supervision o nota |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(RIESGOS, key=lambda x: -residual(x)):
        extra = r.get("supervision") or r.get("nota", "")
        lineas.append(
            f"| {r['id']} | {r['riesgo']} | {cifra(inherente(r))} "
            f"| {r['mitigacion']} | {', '.join(r['evidencia'])} "
            f"| {r['estado']} | {cifra(residual(r))} | {extra} |"
        )
    REGISTRO.parent.mkdir(exist_ok=True)
    REGISTRO.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main(argumentos):
    for r in sorted(RIESGOS, key=lambda x: -residual(x)):
        linea = (
            f"{r['id']} {categoria(inherente(r)):8} -> "
            f"{categoria(residual(r)):8} {r['estado']:10} "
            f"{r['riesgo']}"
        )
        print(textwrap.fill(linea, 70, subsequent_indent=" " * 8))
    if "--escribir" in argumentos:
        escribir_registro()
        print(f"\nRegistro escrito en {REGISTRO}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
