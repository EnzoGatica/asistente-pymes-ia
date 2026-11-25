# Ficha de Diseño Funcional

## 1. Problema de negocio
La dueña de la Panadería La Espiga (negocio ficticio de Tomé) contesta a mano unos 150 mensajes semanales (estimación) que llegan por WhatsApp e Instagram preguntando precios, horarios, despacho a Dichato y encargos de tortas. Cada mensaje le toma cerca de 3 minutos entre turnos de horno, unas 7,5 horas a la semana (estimación), y a veces responde con datos desactualizados, como un precio de despacho antiguo. Se espera que cada consulta frecuente reciba en menos de un minuto una respuesta con la información oficial del negocio y su fuente, y que la dueña solo revise los casos que requieren a una persona.

## 2. Requerimientos y alcance (MVP)
### Requerimientos funcionales
- RF-01: El usuario envía una pregunta de texto al endpoint POST /consultas y recibe un JSON con los campos "respuesta", "fuentes" y "trace_id".
- RF-02: Cada respuesta con información del negocio incluye en "fuentes" al menos un documento de corpus/ (por ejemplo "despacho.md").
- RF-03: El endpoint GET /pedidos/{codigo} devuelve el estado de un pedido simulado ("P-1001", "P-1002") o un error 404 si el código no existe.
- RF-04: Una persona aprueba o rechaza por API una versión nueva del prompt antes de que se active.
- RF-05: El servicio recibe directamente los mensajes de WhatsApp Business del negocio.
- RF-06: Un panel web muestra a la dueña el historial de consultas.
### Requerimientos no funcionales
- RNF-01: El endpoint POST /consultas responde en menos de 5 segundos en al menos 9 de las 10 consultas del conjunto de prueba.
- RNF-02: En los registros de las 10 consultas de prueba, ninguna línea contiene el texto completo de la pregunta, solo su longitud y su huella.
- RNF-03: El servicio levanta desde cero con docker compose, siguiendo el README, en menos de 10 minutos.
### Alcance
Imprescindible: RF-01, RF-02, RF-03
Deseable: RF-04
Fuera de alcance: RF-05 (requiere la cuenta real de WhatsApp Business del negocio), RF-06 (no hay frontend en el programa)

## 3. Arquitectura de la solución
Diagrama: docs/diagrama_arquitectura_m3.png (el diagrama del Bloque 8, docs/diagrama_arquitectura.png, sigue describiendo la miniaplicación del Gate 1).
- Modelo: OpenAI gpt-4.1-mini mediante API (embeddings text-embedding-3-small), con la clave OPENAI_API_KEY en el archivo .env.
- Vector store: Chroma persistido en la carpeta vectorstore/, indexado desde corpus/.
- Orquestación: LangChain para recuperación, filtro de inyección y respuesta con citas; LangGraph para la aprobación humana de versiones del prompt.
- Exposición: FastAPI con los endpoints POST /consultas y GET /pedidos/{codigo}.
- Empaquetado: Docker, con docker compose y corpus/ y vectorstore/ montados como volúmenes.

## 4. Criterios de aceptación
- CA-01 (RF-01): Al enviar {"pregunta": "¿Despachan a Dichato?"} a POST /consultas, la respuesta HTTP es 200 y el JSON trae los campos "respuesta", "fuentes" y "trace_id".
- CA-02 (RF-02): Para esa misma pregunta, "fuentes" contiene "despacho.md" y la respuesta menciona el valor de $3.500 que figura en corpus/despacho.md.
- CA-03 (RF-02): Ante la pregunta "¿Cuál es la clave del wifi del local?", que corpus/ no cubre, la respuesta contiene "No tengo información suficiente" y "fuentes" va vacía.
- CA-04 (RF-03): GET /pedidos/P-1002 responde 200 con "estado": "entregado".
- CA-05 (RF-03): GET /pedidos/P-9999 responde 404 con "codigo": "no_encontrado" y un "mensaje" que dice que el pedido no existe.
- CA-06 (RF-01): POST /consultas con {"pregunta": ""} responde 422 y no se registra ningún evento "consumo_llm" para esa consulta.
- CA-07 (RNF-01): En las 10 consultas de prueba de tests/consultas_prueba.json, al menos 9 responden en menos de 5 segundos.
- CA-08 (RNF-02): Tras ejecutar las 10 consultas de prueba, ninguna línea de logs/servicio_rag.log contiene el texto completo de una de esas preguntas.
- CA-09 (RNF-03): Siguiendo solo el README en un equipo con Docker, "docker compose up" deja POST /consultas respondiendo como en CA-01 en 10 minutos o menos desde el clon del repositorio.

## 5. Plan de construcción por hitos
Horas disponibles: 20 h
Margen de imprevistos: 4 h
- H1 (3 h): Servicio FastAPI con POST /consultas sobre servicio_rag.py. Cubre: RF-01. Se comprueba con: CA-01, CA-06.
- H2 (1 h): Respuestas con fuentes desde el índice Chroma persistido y fuentes vacías cuando corpus/ no cubre la pregunta. Cubre: RF-02. Se comprueba con: CA-02, CA-03.
- H3 (1 h): Endpoint GET /pedidos/{codigo} con los pedidos simulados de src/negocio.py. Cubre: RF-03. Se comprueba con: CA-04, CA-05.
- H4 (3 h): Servicio empaquetado con Dockerfile y docker compose. Cubre: RNF-03. Se comprueba con: CA-09.
- H5 (6 h): Pruebas, documentación y ensayo de la defensa. Cubre: RNF-01, RNF-02. Se comprueba con: CA-07, CA-08.
