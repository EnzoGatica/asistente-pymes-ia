# Bitácora de ajustes

Ejecución de extremo a extremo con `escenarios.py` (14 escenarios en 6 categorías) y `ejecutar_escenarios.py`, contra la API y la interfaz. Las cifras "Antes" se midieron el 25-11-2026 volviendo temporalmente al código previo a cada cambio, con los mismos 14 escenarios; "Después" es la corrida con el cambio aplicado.

| Iteración | Qué falló | Palanca | Cambio | Antes | Después | Decisión |
|---|---|---|---|---|---|---|
| 1 | E-01 a E-07 y E-12: toda consulta al modelo respondía 503 (OpenAI devuelve 404 "gpt-4.1-nano has been deprecated") | configuración | MODELO pasa de gpt-4.1-nano a gpt-4.1-mini, el respaldo previsto en docs/decision-arquitectura.md | 6 de 14 | 12 de 14 | conservar |
| 2 | E-06 y E-07: el modelo decía "no contamos con información" pero la respuesta citaba horarios.md y sobre_nosotros.md | componente | servicio_rag.py reconoce cuando el modelo declara que no tiene la información y responde el mensaje estándar con fuentes vacías (prueba parcial tests/parciales/test_sin_cobertura.py) | 12 de 14 | 14 de 14 | conservar |

Cada cambio se probó primero con una prueba que fallaba (tests/test_gate2.py::test_6 para la iteración 2) y después con los 14 escenarios completos.
