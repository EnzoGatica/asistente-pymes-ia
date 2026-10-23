# Decisión de personalización: asistente de atención de pymes

Generado con [`decision.py`](decision.py) (esqueleto en `decision_personalizacion_esqueleto.md`) y completado a mano el 22-10-2026.

## 1. El problema

El asistente tiene que responder con los datos **vigentes** de cada negocio (precios, horarios, despachos, políticas de reclamos), y esos datos cambian: la panadería de ejemplo actualiza precios el primer día hábil de cada mes. Sin esos datos, el modelo base no puede saber cuánto vale la torta selva negra ni si se despacha a Penco.

## 2. Resultado del método de decisión

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿La información cambia seguido? | Sí | `corpus/productos_precios.md`: los precios cambian una vez al mes, y los horarios de feriados y los productos de temporada cambian varias veces al año. |
| ¿Hay un problema de formato o tono (≥ 15 %)? | No | De 20 respuestas reales (`resultados_metricas.json`), 2 (10 %) fallan el tono por hablar en tercera persona ("Abren a las 8:00") y ninguna supera las 2 frases. El JSON con `json_schema` dio 9/9 salidas válidas (`prompts/registro_resultados.json`). |
| ¿Dataset grande y de calidad (≥ 200)? | No | `datos/dataset_tuning.jsonl` tiene 17 ejemplos validados. |
| ¿Presupuesto limitado o se necesita iterar rápido? | Sí | El cliente es una pyme y un cambio de precio tiene que verse el mismo día. |
| ¿Se necesitan varias variantes del modelo? | No | Es un solo comportamiento; lo que cambia entre negocios es la información, no la forma de responder. |

Puntaje: **RAG 5 puntos**, PEFT 1 punto, fine-tuning completo 0 puntos. Ganador claro, sin empate.

Sensibilidad: si el tono fallara en el 15 % o más de las respuestas, el resultado sería RAG 5, PEFT 3 y fine-tuning 1. RAG seguiría ganando, pero PEFT pasaría a ser un complemento razonable.

## 3. Técnica elegida y por qué

**RAG**, que ya está construido en la Unidad 2.5 (`src/indexar_corpus.py`, `src/recuperacion.py`): lo que le falta al modelo es información que cambia cada mes, y con RAG actualizar un precio es editar un `.md` y reindexar en segundos, sin entrenar nada.

Descarto el fine-tuning completo y PEFT porque el problema no es de comportamiento: el formato ya es consistente con `json_schema` y el 10 % de fallas de tono se corrige más barato ajustando el prompt de sistema ("habla en primera persona plural, como el negocio") y midiendo de nuevo. Además, un modelo entrenado con los precios de octubre daría precios viejos en noviembre.

## 4. Qué necesitaría para ejecutarla

- **Corpus:** hoy hay 8 documentos (16 chunks) de un negocio de ejemplo. Para un cliente real faltan sus 8 documentos equivalentes: unas **2 horas** de entrevista con el dueño para levantar horarios, precios, despacho, pagos, reclamos e ingredientes, y **30 minutos** para escribirlos.
- **Mantención:** **15 minutos al mes** para actualizar `productos_precios.md` y correr `python src/indexar_corpus.py` (tarda menos de 5 segundos y cuesta menos de USD 0,001 en embeddings).
- **Calidad:** volver a correr `python src/evaluacion_recuperacion.py` con cada corpus nuevo, con la meta de mantener el recall@3 en 1,0 (hoy: precisión 0,361 y recall 1,000 en 12 preguntas).
- **Si algún día hiciera falta PEFT para el tono:** se necesitan al menos 200 ejemplos; hay 17, así que faltan **183**, unas **15 horas** de etiquetado a 5 minutos por ejemplo. No se justifica mientras las fallas de tono estén bajo el 15 %.
