"""Comprueba /docs y los criterios CA-01 a CA-06 de docs/ficha_diseno_funcional.md contra la lógica real.

CA-01, CA-02 y CA-03 llaman a OpenAI: necesitan OPENAI_API_KEY en .env (cuestan fracciones de centavo).
"""
from fastapi.testclient import TestClient

from servicio.main import app

cliente = TestClient(app, raise_server_exceptions=False)
PREGUNTA = "¿Despachan a Dichato?"


def esquema():
    return cliente.get("/openapi.json").json()


def docs_navegables():
    r = cliente.get("/docs")
    if r.status_code != 200:
        return False, f"/docs responde {r.status_code}"
    return True, f"rutas documentadas: {sorted(esquema()['paths'])}"


def campos_documentados():
    esquemas = esquema()["components"]["schemas"]
    sin = [
        f"{nombre}.{campo}"
        for nombre in ("Consulta", "Respuesta", "EstadoPedido", "Error")
        for campo, datos in esquemas[nombre]["properties"].items()
        if "description" not in datos
    ]
    if sin:
        return False, f"sin descripcion: {sin}"
    return True, "todos los campos tienen descripcion"


def ca_01():
    r = cliente.post("/consultas", json={"pregunta": PREGUNTA})
    ok = r.status_code == 200 and set(r.json()) == {"respuesta", "fuentes", "trace_id"}
    return ok, f"estado {r.status_code}, campos {sorted(r.json())}"


def ca_02():
    datos = cliente.post("/consultas", json={"pregunta": PREGUNTA}).json()
    ok = "despacho.md" in datos["fuentes"] and "3.500" in datos["respuesta"]
    return ok, f"fuentes: {datos['fuentes']}"


def ca_03():
    datos = cliente.post("/consultas", json={"pregunta": "¿Cuál es la clave del wifi del local?"}).json()
    ok = datos["fuentes"] == [] and "No tengo información suficiente" in datos["respuesta"]
    return ok, f"fuentes: {datos['fuentes']}"


def ca_04():
    r = cliente.get("/pedidos/P-1002")
    return r.status_code == 200 and r.json()["estado"] == "entregado", f"estado: {r.json().get('estado')}"


def ca_05():
    r = cliente.get("/pedidos/P-9999")
    datos = r.json()
    ok = r.status_code == 404 and datos["codigo"] == "no_encontrado" and "no existe" in datos["mensaje"]
    return ok, f"{r.status_code}: {datos}"


def ca_06():
    r = cliente.post("/consultas", json={"pregunta": ""})
    return r.status_code == 422, f"{r.status_code}: {r.json()['codigo']}"


COMPROBACIONES = [
    ("DOC-1", "documentacion en /docs", docs_navegables),
    ("DOC-2", "campos documentados", campos_documentados),
    ("CA-01", "respuesta, fuentes y trace_id", ca_01),
    ("CA-02", "fuente despacho.md y $3.500", ca_02),
    ("CA-03", "sin cobertura: no inventa fuentes", ca_03),
    ("CA-04", "estado del pedido simulado", ca_04),
    ("CA-05", "pedido inexistente: 404", ca_05),
    ("CA-06", "pregunta vacia: 422", ca_06),
]


def ejecutar(comprobaciones):
    cumplidas = 0
    for id_, descripcion, prueba in comprobaciones:
        try:
            ok, evidencia = prueba()
        except Exception as error:
            ok = False
            evidencia = f"error: {type(error).__name__}({error})"
        estado = "PASA " if ok else "FALLA"
        print(f"{estado} {id_} {descripcion} -> {evidencia}")
        cumplidas += 1 if ok else 0
    print(f"\n{cumplidas} de {len(comprobaciones)} comprobaciones cumplidas")
    return cumplidas == len(comprobaciones)


if __name__ == "__main__":
    raise SystemExit(0 if ejecutar(COMPROBACIONES) else 1)
