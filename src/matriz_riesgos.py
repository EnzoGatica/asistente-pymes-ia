"""Matriz de riesgos del asistente de pymes (servicio RAG + agente), con puntaje, categoría y supervisión."""


def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    for p2, i2 in [(probabilidad + 1, impacto), (probabilidad - 1, impacto), (probabilidad, impacto + 1), (probabilidad, impacto - 1)]:
        if 1 <= p2 <= 5 and 1 <= i2 <= 5 and categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


mis_riesgos = [
    {"riesgo": "El asistente informa un precio u horario viejo porque el corpus no se actualizó a inicio de mes",
     "probabilidad": 4,  # los precios cambian todos los meses y la actualización es manual
     "impacto": 3,       # el cliente llega esperando otro precio: se pierde confianza, no dinero directo
     "mitigacion": "Corpus versionado en Git y reindexación en segundos (Bloque 24); evaluación de recuperación (Bloque 27)",
     "supervision": "El dueño revisa y aprueba el diff de corpus/ antes de reindexar, el primer día hábil de cada mes"},
    {"riesgo": "Inyección de prompt escrita en un documento del corpus o en el mensaje de un cliente",
     "probabilidad": 3,  # el corpus lo escribe el negocio, pero el mensaje del cliente es texto libre
     "impacto": 4,       # podría hacer que el asistente prometa descuentos o revele instrucciones
     "mitigacion": "Filtro de patrones sobre los documentos recuperados (Bloque 31) + prompt v2 que delimita el contexto como datos (Bloque 32)",
     "supervision": "Revisión diaria de los eventos documento_descartado_por_inyeccion en logs/servicio_rag.log"},
    {"riesgo": "El agente genera un reembolso indebido a partir de un reclamo falso",
     "probabilidad": 2,  # la herramienta solo se usa si el cliente lo pide explícitamente
     "impacto": 5,       # dinero que sale del negocio y no se recupera
     "mitigacion": "generar_reembolso exige esperar_aprobacion, con tope por pedido y $50.000 (Bloque 23)",
     "supervision": "Aprobación humana obligatoria del dueño en cada reembolso; sin respuesta en 60 s se rechaza"},
    {"riesgo": "Datos personales de clientes (correo, teléfono, dirección) quedan en texto plano en los logs",
     "probabilidad": 3,  # los clientes escriben sus datos en la misma pregunta
     "impacto": 4,       # incumple la Ley 19.628 de protección de la vida privada
     "mitigacion": "Logs con solo longitudes, conteos y huella de la pregunta (Bloque 31); test_3 de tests/test_gate2.py",
     "supervision": "Chequeo semanal: grep de correos y teléfonos sobre logs/; si aparece uno, se corta el logger y se borra el archivo"},
    {"riesgo": "Una versión nueva del prompt empeora las respuestas (deja de citar o inventa datos)",
     "probabilidad": 3,  # el prompt se ajusta cada vez que aparece una falla de tono o formato
     "impacto": 3,       # respuestas sin cita equivalen a alucinaciones para el cliente
     "mitigacion": "Registro de versiones con huella y diff (Bloque 32); el servicio agrega las fuentes si la respuesta no las cita",
     "supervision": "Grafo de despliegue con interrupt(): ninguna huella nueva se activa sin Command(resume=True)"},
    {"riesgo": "Caída o límite de uso (429) de la API de OpenAI en hora punta",
     "probabilidad": 2,  # en las pruebas, 40 consultas concurrentes no gatillaron un 429
     "impacto": 3,       # el cliente no recibe respuesta y el negocio contesta a mano
     "mitigacion": "Reintento con backoff exponencial (Bloque 13) y respuesta segura sin traceback (Bloque 20)",
     "supervision": "No requiere aprobación: es MEDIO; se revisa el conteo de errores en la revisión semanal de logs"},
]

for r in mis_riesgos:
    r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
    r["categoria"] = categoria_riesgo(r["puntaje"])
    r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])

if __name__ == "__main__":
    for r in sorted(mis_riesgos, key=lambda x: -x["puntaje"]):
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}")
        print(f"           mitigación: {r['mitigacion']}")
        print(f"           supervisión: {r['supervision']}")
    print()
    for r in mis_riesgos:
        if r["al_limite"]:
            print("revisar con otra persona:", r["riesgo"])
    sin_supervision = [r["riesgo"] for r in mis_riesgos if r["categoria"] in ("ALTO", "CRITICO") and not r["supervision"]]
    assert not sin_supervision, f"riesgos ALTO/CRITICO sin supervisión: {sin_supervision}"
