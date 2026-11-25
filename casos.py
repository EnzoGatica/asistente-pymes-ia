"""Tabla de casos de la API: la usan tests/test_api.py, cliente_externo.py y registrar_pruebas.py."""

CASOS = [
    {"id": "V-01", "descripcion": "CA-01/CA-02: consulta cubierta por corpus/", "metodo": "POST",
     "ruta": "/consultas", "json": {"pregunta": "¿Despachan a Dichato?"}, "estado": 200, "contiene": "despacho.md"},
    {"id": "V-02", "descripcion": "CA-03: consulta sin cobertura en corpus/ (resultado vacío)", "metodo": "POST",
     "ruta": "/consultas", "json": {"pregunta": "¿Cuál es la clave del wifi del local?"}, "estado": 200,
     "contiene": '"fuentes":[]'},
    {"id": "V-03", "descripcion": "CA-04: estado de un pedido existente", "metodo": "GET",
     "ruta": "/pedidos/P-1002", "estado": 200, "contiene": "entregado"},
    {"id": "V-04", "descripcion": "comprobación de salud", "metodo": "GET", "ruta": "/salud", "estado": 200,
     "contiene": "ok"},
    {"id": "I-01", "descripcion": "falta el campo pregunta", "metodo": "POST", "ruta": "/consultas", "json": {},
     "estado": 422, "contiene": "pregunta: Field required"},
    {"id": "I-02", "descripcion": "CA-06: pregunta vacía", "metodo": "POST", "ruta": "/consultas",
     "json": {"pregunta": ""}, "estado": 422, "contiene": "at least 3 characters"},
    {"id": "I-03", "descripcion": "pregunta solo con espacios", "metodo": "POST", "ruta": "/consultas",
     "json": {"pregunta": "    "}, "estado": 422, "contiene": "at least 3 characters"},
    {"id": "I-04", "descripcion": "pregunta de 600 caracteres", "metodo": "POST", "ruta": "/consultas",
     "json": {"pregunta": "a" * 600}, "estado": 422, "contiene": "at most 500 characters"},
    {"id": "I-05", "descripcion": "tipo incorrecto en pregunta", "metodo": "POST", "ruta": "/consultas",
     "json": {"pregunta": 123}, "estado": 422, "contiene": "valid string"},
    {"id": "I-06", "descripcion": "cuerpo que no es JSON válido", "metodo": "POST", "ruta": "/consultas",
     "contenido": '{"pregunta": "hola', "estado": 422, "contiene": "entrada_invalida"},
    {"id": "I-07", "descripcion": "código de pedido mal formado", "metodo": "GET", "ruta": "/pedidos/ABC",
     "estado": 422, "contiene": "entrada_invalida"},
    {"id": "I-08", "descripcion": "CA-05: pedido que no existe", "metodo": "GET", "ruta": "/pedidos/P-9999",
     "estado": 404, "contiene": "no existe"},
    {"id": "I-09", "descripcion": "método no permitido", "metodo": "GET", "ruta": "/consultas", "estado": 405,
     "contiene": "metodo_no_permitido"},
    {"id": "I-10", "descripcion": "ruta que no existe", "metodo": "GET", "ruta": "/ruta-inexistente",
     "estado": 404, "contiene": "no_encontrado"},
]


def ejecutar_caso(cliente, caso):
    """Envia el caso con cualquier cliente que tenga .request()."""
    if "contenido" in caso:
        r = cliente.request(
            caso["metodo"],
            caso["ruta"],
            content=caso["contenido"],
            headers={"Content-Type": "application/json"},
        )
    else:
        r = cliente.request(
            caso["metodo"], caso["ruta"], json=caso.get("json")
        )
    ok = r.status_code == caso["estado"] and caso["contiene"] in r.text
    return ok, r.status_code, r.text
