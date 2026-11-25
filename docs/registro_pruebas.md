# Registro de pruebas de la API
Fecha: 2026-11-25
Servicio probado: http://127.0.0.1:8000 (cliente: httpx2)
Resultado: 14 de 14 casos cumplidos

| Caso | Descripción | Petición | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| V-01 | CA-01/CA-02: consulta cubierta por corpus/ | POST /consultas {"pregunta": "¿Despachan a Dichato?"} | 200 | 200 | PASA |
| V-02 | CA-03: consulta sin cobertura en corpus/ (resultado vacío) | POST /consultas {"pregunta": "¿Cuál es la clave del wifi... | 200 | 200 | PASA |
| V-03 | CA-04: estado de un pedido existente | GET /pedidos/P-1002 | 200 | 200 | PASA |
| V-04 | comprobación de salud | GET /salud | 200 | 200 | PASA |
| I-01 | falta el campo pregunta | POST /consultas {} | 422 | 422 | PASA |
| I-02 | CA-06: pregunta vacía | POST /consultas {"pregunta": ""} | 422 | 422 | PASA |
| I-03 | pregunta solo con espacios | POST /consultas {"pregunta": "    "} | 422 | 422 | PASA |
| I-04 | pregunta de 600 caracteres | POST /consultas {"pregunta": "aaaaaaaaaaaaaaaaaaaaaaaaaa... | 422 | 422 | PASA |
| I-05 | tipo incorrecto en pregunta | POST /consultas {"pregunta": 123} | 422 | 422 | PASA |
| I-06 | cuerpo que no es JSON válido | POST /consultas {"pregunta": "hola | 422 | 422 | PASA |
| I-07 | código de pedido mal formado | GET /pedidos/ABC | 422 | 422 | PASA |
| I-08 | CA-05: pedido que no existe | GET /pedidos/P-9999 | 404 | 404 | PASA |
| I-09 | método no permitido | GET /consultas | 405 | 405 | PASA |
| I-10 | ruta que no existe | GET /ruta-inexistente | 404 | 404 | PASA |
