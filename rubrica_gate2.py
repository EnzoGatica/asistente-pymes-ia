"""Autoevaluación honesta contra la rúbrica del Gate 2 (promedio ponderado + criterios no compensables)."""


def promedio_ponderado(puntajes, pesos):
    return sum(puntajes[d] * pesos[d] for d in pesos)


pesos = {
    "pipeline_funcional": 0.25, "recuperacion_citacion": 0.15,
    "costo_latencia": 0.10, "personalizacion": 0.15,
    "observabilidad": 0.15, "seguridad_gobernanza": 0.20,
}

mi_puntaje = {
    # servicio_rag.py indexa (incremental), recupera y responde; 70 pruebas en verde
    "pipeline_funcional": 95,
    # recall@3 = 1.000 pero precisión@3 = 0.361: con un solo chunk relevante por pregunta el techo es 0.33
    "recuperacion_citacion": 85,
    # registros reales por etapa y por k en registros_latencia_costo.jsonl
    "costo_latencia": 90,
    # decision_personalizacion.md con evidencia propia; el dataset PEFT tiene 17 de 200 ejemplos
    "personalizacion": 90,
    # trace_id por consulta, consumo por llamada, logs JSON en consola y archivo
    "observabilidad": 90,
    # filtro por patrones es lista negra (limitación declarada); supervisión del despliegue y del reembolso
    "seguridad_gobernanza": 85,
}

no_compensables = {
    "pipeline_corre_de_punta_a_punta": True,   # tests/test_gate2.py::test_1 + corrida real con exit 0
    "respuestas_citan_fuente": True,           # test_2 y test_2b (asegurar_cita agrega fuentes si faltan)
    "logs_sin_contenido_crudo": True,          # test_3 + grep de ana.perez sobre logs/ sin resultados
    "supervision_humana_funciona": True,       # test_4 y test_4b (aprobación y rechazo con interrupt/Command)
}

if __name__ == "__main__":
    print("suma de pesos:", round(sum(pesos.values()), 2))
    promedio = promedio_ponderado(mi_puntaje, pesos)
    todos_ok = all(no_compensables.values())
    print(f"promedio: {promedio:.1f}, no compensables OK? {todos_ok} -> aprueba? {promedio >= 80 and todos_ok}")
