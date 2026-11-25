"""Matriz de Pruebas del asistente: válidos, inválidos y de borde.

Cada escenario declara la petición, lo que se espera (escrito desde la ficha antes de ejecutar)
y qué requisito o criterio de docs/ficha_diseno_funcional.md cubre. Se ejecuta con ejecutar_matriz.py.
"""

MATRIZ = [
    {
        "id": "MP-01",
        "tipo": "valido",
        "escenario": "mayúsculas y espacios sobrantes",
        "peticion": {"metodo": "POST", "ruta": "/consultas", "json": {"pregunta": "   ¿DESPACHAN A DICHATO?   "}},
        "esperado": {"estado": 200, "contiene": ["3.500", "despacho.md"]},
        "cubre": ["RF-01", "RF-02", "CA-02"],
    },
    {
        "id": "MP-02",
        "tipo": "invalido",
        "escenario": "cuerpo sin el campo pregunta",
        "peticion": {"metodo": "POST", "ruta": "/consultas", "json": {}},
        "esperado": {"estado": 422, "contiene": ["pregunta"]},
        "cubre": ["RF-01"],
    },
    {
        "id": "MP-03",
        "tipo": "borde",
        "escenario": "501 caracteres, uno sobre el límite",
        "peticion": {"metodo": "POST", "ruta": "/consultas", "json": {"pregunta": "a" * 501}},
        "esperado": {"estado": 422, "contiene": ["500"]},
        "cubre": ["RF-01"],
    },
    {
        "id": "MP-04",
        "tipo": "borde",
        "escenario": "pedido bien escrito que no existe",
        "peticion": {"metodo": "GET", "ruta": "/pedidos/P-9999"},
        "esperado": {"estado": 404, "contiene": ["no_encontrado"]},
        "cubre": ["RF-03", "CA-05"],
    },
    {
        "id": "MP-05",
        "tipo": "invalido",
        "escenario": "pregunta hecha solo de espacios",
        "peticion": {"metodo": "POST", "ruta": "/consultas", "json": {"pregunta": "     "}},
        "esperado": {"estado": 422, "contiene": ["entrada_invalida"]},
        "cubre": ["RF-01", "CA-06"],
    },
    {
        "id": "MP-06",
        "tipo": "borde",
        "escenario": "pregunta que corpus/ no cubre",
        "peticion": {"metodo": "POST", "ruta": "/consultas", "json": {"pregunta": "¿Cuál es la clave del wifi del local?"}},
        "esperado": {"estado": 200, "contiene": ["No tengo información suficiente"], "fuentes": []},
        "cubre": ["RF-02", "CA-03"],
    },
]
