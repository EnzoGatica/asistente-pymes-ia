# Decisiones de arquitectura

Cada decisión dice qué se decidió, por qué, qué se descartó y qué cuesta. El README las resume; aquí está el detalle. Los ID no se reutilizan: una decisión reemplazada queda registrada con su estado.

## D-01 RAG sobre corpus/ con Chroma, sin fine-tuning

- **Estado:** vigente
- **Contexto:** La información del negocio (precios, horarios, despacho) cambia cada mes y vive en 8 documentos cortos que la dueña puede editar. Las respuestas deben citar de dónde sale cada dato.
- **Decisión:** Se indexa corpus/ en Chroma con embeddings text-embedding-3-small; el índice persiste en vectorstore/ y solo se actualizan los fragmentos que cambiaron. Cada consulta recupera 3 fragmentos y el modelo responde citando su fuente.
- **Alternativas descartadas:** Fine-tuning o PEFT: cada cambio de precio exigiría reentrenar y no da citas (comparación en decision_personalizacion.md). Búsqueda por palabras clave: no entiende sinónimos como "despacho" y "envío".
- **Costo:** La indexación y cada consulta dependen de la API de embeddings de OpenAI, y una pregunta que corpus/ no cubre no se puede responder aunque el dato sea obvio para la dueña.

## D-02 Modelo gpt-4.1-nano por costo

- **Estado:** reemplazada
- **Contexto:** Respuestas de una a tres frases para cientos de consultas al mes de una pyme que paga poco.
- **Decisión:** Se eligió gpt-4.1-nano por costar ~3,7 veces menos que gpt-4.1-mini con calidad equivalente en respuestas cortas (docs/decision-arquitectura.md, Bloque 9).
- **Alternativas descartadas:** gpt-4.1-mini: calidad extra que no se nota en dos frases, a casi cuatro veces el costo. Quedó como respaldo en la misma constante.
- **Costo:** OpenAI lo dio de baja en noviembre de 2026 y el servicio respondió 503 en todas las consultas hasta cambiarlo. La reemplaza D-03.

## D-03 Modelo gpt-4.1-mini en una sola constante, con falla a la vista

- **Estado:** vigente
- **Contexto:** El modelo original fue dado de baja (D-02) y el proveedor puede volver a hacerlo o dejar de responder.
- **Decisión:** MODELO en src/consumir_openai.py vale gpt-4.1-mini. Si el proveedor no responde, la API devuelve 503 con un mensaje estándar en vez de un traceback o una respuesta inventada; /salud dice si hay clave.
- **Alternativas descartadas:** Responder con un texto genérico sin avisar: oculta el problema a la dueña. Usar varios proveedores con conmutación automática: más claves, más costo y más código para un volumen chico.
- **Costo:** Cuesta unos USD 0,08 por cada 1.000 consultas en vez de 0,02, y sin OpenAI el servicio no responde consultas (los pedidos sí, porque son datos simulados).

## D-04 Si el contexto no alcanza, no se citan fuentes

- **Estado:** vigente
- **Contexto:** El modelo a veces dice "no contamos con información" y aun así el servicio le agregaba fuentes, lo que hacía ver respaldado algo que no lo estaba (E-06 y E-07 en docs/bitacora_ajustes.md).
- **Decisión:** servicio_rag.py reconoce cuando el modelo declara que no tiene la información (DECLARA_SIN_INFO) y responde el mensaje estándar con fuentes vacías para que intervenga una persona.
- **Alternativas descartadas:** Pedir al modelo un JSON con un campo "cubierto": cambia el prompt versionado y su aprobación humana. Comparar cada cifra con el contexto: bloquea precios calculados legítimos, como la selva negra con recargo.
- **Costo:** Solo reconoce frases conocidas ("no tengo información", "no contamos con información"); un precio inventado con cita no se detecta. Lo declara LIM-02.

## D-05 Un contrato en cada borde y errores uniformes

- **Estado:** vigente
- **Contexto:** La pregunta llega de clientes por canales abiertos y no es de fiar; los errores no deben revelar detalles internos ni repetir lo enviado.
- **Decisión:** pydantic valida la pregunta (3 a 500 caracteres, espacios recortados) y el código de pedido (P-0000). Todos los errores 404, 405, 422, 500 y 503 tienen la forma "codigo" y "mensaje" (servicio/errores.py).
- **Alternativas descartadas:** Validar dentro de servicio_rag.py: el modelo se llamaría con entradas basura y se pagaría por ellas. Dejar los errores por defecto de FastAPI: repiten el valor enviado y cambian de forma según la ruta.
- **Costo:** Los mensajes de validación vienen de pydantic en inglés ("String should have at least 3 characters") y la interfaz los muestra tal cual.

## D-06 Defensa en capas contra la inyección

- **Estado:** vigente
- **Contexto:** corpus/ podría incluir texto de terceros (por ejemplo reseñas) con órdenes escondidas, y una instrucción en el prompt no obliga al modelo.
- **Decisión:** Un filtro de patrones descarta los fragmentos recuperados con órdenes; el prompt v2 encierra el contexto entre etiquetas y lo trata como datos; los registros guardan longitud y huella, nunca el texto de la pregunta.
- **Alternativas descartadas:** Solo el prompt: el modelo puede ignorarlo. Un clasificador con el propio modelo en cada fragmento: duplica el costo y la latencia de cada consulta.
- **Costo:** El filtro lee patrones y no reconoce una orden redactada con otras palabras. Lo declara LIM-01, con revisión de la dueña antes de enviar.

## D-07 Dos contenedores y la clave solo al ejecutar

- **Estado:** vigente
- **Contexto:** La interfaz es una pieza de demostración y no debe tocar el modelo ni la clave; la imagen no puede llevar secretos.
- **Decisión:** api e interfaz son dos servicios de compose.yaml; la interfaz llama a la API por la red interna. OPENAI_API_KEY entra por variables de entorno al arrancar y buscar_secretos.py revisa archivos, git y la imagen.
- **Alternativas descartadas:** Una sola imagen con todo: la interfaz heredaría la clave. Pasar la clave con ARG o ENV en el Dockerfile: queda guardada en las capas de la imagen.
- **Costo:** Dos imágenes que construir y mantener, y la interfaz debe esperar a que la API esté sana para arrancar.
