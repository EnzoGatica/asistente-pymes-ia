# Límites de la métrica de evaluación

Pipeline evaluado: `src/pipeline_texto.py` (`procesar_texto` + `calcular_precision_cobertura_f1`), aplicado por `src/evaluar_salidas.py` a 20 respuestas reales del asistente de la panadería ([resultados_metricas.json](../resultados_metricas.json)). Revisión manual en [revision_manual.py](../revision_manual.py) / `revision_manual.json`.

Resultado global (22-10-2026): precisión promedio 0,74 · cobertura promedio 0,83 · **F1 promedio 0,77**.

## Qué mide

Cuántas palabras (contando repeticiones) comparten la respuesta del modelo y una referencia escrita a mano, después de pasar ambas a minúsculas y quitarles la puntuación: la precisión castiga las palabras de más y la cobertura, las que faltan.

## Modos de falla conocidos

- **Respuestas correctas con F1 bajo por paráfrasis o por ser más acotadas que la referencia.** "¿Puedo pagar con tarjeta de crédito?" → "Sí, aceptamos pago con tarjeta de crédito." tiene F1 = 0,43 y es correcta: la referencia enumeraba todos los medios de pago. Lo mismo con "¿Tienen estacionamiento?" (F1 = 0,55): reconocer que no hay dato es lo correcto, pero se redactó distinto.
- **Información extra correcta y útil baja la precisión.** "Quiero una torta para 30 personas" (F1 = 0,67) agrega que hay que encargarla con 48 h de anticipación; para el cliente es mejor respuesta, para la métrica es ruido.
- **Los números se parten en tokens y un precio equivocado puntúa alto.** "$2.200" queda como `2` y `200`. Probado aparte: la referencia "$2.200" contra una respuesta con "$2.000" da **F1 = 0,86**. Para un negocio, un precio equivocado es el peor error posible, y la métrica casi no lo ve.
- **No detecta negaciones.** "Sí, despachamos a Dichato" contra "No, no despachamos a Dichato" da **F1 = 0,67**, aunque dice exactamente lo contrario.
- **No mide omisiones que la referencia tampoco tiene.** "¿Cuánto cuesta la torta para 15 personas?" saca F1 = 1,0 pero no avisa de las 48 h de anticipación; la métrica solo es tan buena como la referencia.
- **No evalúa tono ni voz.** "Abren a las 8:00" (F1 = 0,43) habla en tercera persona en vez de la voz del negocio; eso lo detecta solo la lectura humana.

## Muestra revisada

10 de los 20 casos, revisados a mano con la rúbrica de corrección factual, completitud y contradicción: los **5 de F1 más bajo** (0,43 a 0,60) y **5 de F1 = 1,0**. Hallazgo principal: los 5 casos de F1 bajo eran **correctos** (4 completos y 1 parcial, sin la hora de cierre); ninguno tenía un error factual. En esta muestra, el F1 bajo señaló diferencias de redacción y no errores. Los 5 casos con F1 = 1,0 también eran correctos, pero la prueba aparte con el precio equivocado muestra que un F1 alto no garantiza que los números estén bien.

## Recomendación de uso

- Usar el F1 solo para **comparar versiones** del prompt o del modelo sobre el mismo set de 20 casos (una caída del F1 promedio sobre 0,05 merece revisión), no como nota de calidad de una respuesta individual.
- **Revisar siempre a mano** toda respuesta que contenga precios, horarios o una negación ("no despachamos", "no tenemos"), sin importar su F1: son justo los casos donde la métrica falla y donde un error le cuesta un cliente al negocio.
- Para precios y horarios, agregar en el Módulo 2 una verificación exacta (extraer el número y compararlo con la ficha del negocio) en vez de depender de la coincidencia de palabras.
