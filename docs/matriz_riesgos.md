# Matriz de riesgos

Fecha: 2026-11-25
Huella de la matriz: 9f715c80c22a
Riesgos: 8

| ID | Riesgo | Inherente | Mitigacion | Evidencia | Estado | Residual | Supervision o nota |
|---|---|---|---|---|---|---|---|
| R-01 | Orden escondida en un fragmento de corpus/ (inyeccion indirecta) | 16 CRITICO | Filtro de patrones sobre los fragmentos recuperados y prompt que trata el contexto como datos | ataques:A-01, pruebas:tests/parciales/test_inyeccion.py | parcial | 12 ALTO | La duena revisa cada respuesta antes de enviarla y se amplian los patrones con cada caso nuevo |
| R-02 | Respuesta con un dato que corpus/ no respalda | 16 CRITICO | Prompt que exige usar solo el contexto y deteccion de sin informacion con fuentes vacias | alucinacion:H-01, alucinacion:H-02, pruebas:tests/parciales/test_sin_cobertura.py | parcial | 12 ALTO | La duena revisa cada respuesta antes de enviarla; precios y plazos se confirman contra corpus/ |
| R-08 | El proveedor da de baja el modelo o deja de responder | 12 ALTO | Modelo de respaldo en una sola constante y respuesta 503 controlada, sin detalles internos | pruebas:tests/test_api.py::test_proveedor_caido_responde_503_sin_detalles | verificada | 6 MEDIO |  |
| R-03 | Fuga de la clave de OpenAI | 10 ALTO | Clave solo en variables de entorno, nunca en la imagen, compose.yaml ni git | fuga:F-02, comando:python buscar_secretos.py | verificada | 5 MEDIO |  |
| R-04 | Datos personales de clientes en los registros | 15 CRITICO | Se registran longitud y huella de la pregunta, nunca su texto | fuga:F-01, pruebas:tests/test_gate2.py | verificada | 5 MEDIO |  |
| R-05 | Los errores repiten lo que envio el cliente | 6 MEDIO | Errores uniformes con codigo y mensaje que nombran el campo, no su valor | fuga:F-03 | verificada | 3 BAJO |  |
| R-06 | Entradas malformadas o gigantes tumban el servicio | 9 ALTO | Validacion con pydantic (3 a 500 caracteres, espacios recortados) antes de llamar al modelo | ataques:A-02, matriz:MP-02, matriz:MP-03, matriz:MP-05 | verificada | 3 BAJO |  |
| R-07 | El filtro bloquea preguntas legitimas | 4 MEDIO | El filtro actua sobre los fragmentos recuperados, no sobre la pregunta del cliente | ataques:B-01, ataques:B-02 | verificada | 2 BAJO |  |
