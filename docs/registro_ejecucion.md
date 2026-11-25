<!-- AUTO:INICIO -->
# Registro de la ejecución completa

| Dato | Valor |
|---|---|
| Fecha | 2026-11-25 19:36 |
| Commit del código | c6bb8cc (sin cambios) |
| Destinos | API http://127.0.0.1:8000 e interfaz http://127.0.0.1:8080 |

Escenarios: 14 de 14 cumplidos

Pruebas automáticas: 106 pasan, 0 fallan

## Componentes

| Componente | Modo | Detalle |
|---|---|---|
| Modelo | real | OpenAI gpt-4.1-mini |
| Recuperación | real | Chroma con embeddings text-embedding-3-small sobre corpus/ |
| API | real | FastAPI en contenedor, entorno desarrollo |
| Interfaz | real | FastAPI en contenedor, llama a la API por la red de Compose |
| Pedidos | simulado | datos de src/negocio.py |

## Resultados por escenario

| Escenario | Descripción | Resultado |
|---|---|---|
| E-01 | despacho a Dichato desde la interfaz | pasa |
| E-02 | horario de domingo | pasa |
| E-03 | precio del kilo de marraqueta | pasa |
| E-04 | pago con tarjeta de crédito | pasa |
| E-05 | anticipación para encargar una torta | pasa |
| E-06 | clave del wifi (no está en corpus/) | pasa |
| E-07 | sueldo de los panaderos (no está en corpus/) | pasa |
| E-08 | pregunta vacía en la API | pasa |
| E-09 | pregunta de una letra desde la interfaz | pasa |
| E-10 | pedido que no existe | pasa |
| E-11 | pedido en preparación | pasa |
| E-12 | intento de sacar las instrucciones del sistema | pasa |
| E-13 | salud de la API con modelo configurado | pasa |
| E-14 | salud de la interfaz | pasa |
<!-- AUTO:FIN -->

## Qué se observó

Los 14 escenarios pasaron por la API y por la interfaz con el modelo real (gpt-4.1-mini) en dos corridas seguidas con el mismo resultado. Las consultas cubiertas por corpus/ tardan entre 1,2 y 2 segundos; la primera de la corrida tardó 7 segundos porque abre el índice. Antes de esta corrida aparecieron dos fallas reales, registradas en docs/bitacora_ajustes.md: el modelo original fue dado de baja por OpenAI (6 de 14) y el servicio citaba fuentes cuando el modelo decía no tener la información (12 de 14).

## Qué no se probó

No se usó ningún componente de respaldo: el modelo, la recuperación, la API y la interfaz corrieron reales; solo los pedidos son datos simulados. No se probó con varios usuarios a la vez ni con preguntas fuera de las 14 de escenarios.py, ni el comportamiento cuando OpenAI responde lento o con límite de uso (el servicio devuelve 503, cubierto solo en tests/test_api.py con un modelo simulado). Tampoco se probó la detección de "sin información" con frases distintas a las que reconoce DECLARA_SIN_INFO.

## Siguiente paso

Que otra persona clone el repositorio y repita la corrida siguiendo solo el README (verificación cruzada pendiente), y ampliar escenarios.py con preguntas reales de clientes para medir con más casos la detección de "sin información" y el filtro de inyección.
