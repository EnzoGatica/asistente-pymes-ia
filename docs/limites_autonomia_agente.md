# Límites de autonomía: agente de atención de la Panadería La Espiga

Agente: [`src/agente.py`](../src/agente.py) (`create_tool_calling_agent` + `AgentExecutor`, `gpt-4.1-nano`, memoria por `session_id`). Trazas reales: [`trazas_agente.jsonl`](../trazas_agente.jsonl) (8 interacciones del 22-10-2026, salida de consola en [`evidencia_agente.txt`](evidencia_agente.txt)).

## Herramientas y nivel de riesgo

- `consultar_precio`: **bajo** (solo lectura). Lee la lista de precios y no modifica nada; un error deja al cliente con un precio mal informado, pero el precio que se cobra lo define la caja, no el agente.
- `calcular_total_pedido`: **bajo** (solo cálculo). No registra el pedido ni cobra; si no hay despacho a la comuna lo dice y no inventa una tarifa.
- `consultar_estado_pedido`: **bajo** (solo lectura). Devuelve el estado y, si se pide, el historial de un pedido. Riesgo residual: cualquiera que conozca un número de pedido puede ver su estado (no expone nombre, dirección ni pago).
- `generar_reembolso`: **alto** (escritura irreversible con impacto económico). Devuelve dinero del negocio; un reembolso mal hecho no se recupera.

No hay herramientas de escritura reversible (por ejemplo, "registrar pedido"): se dejó fuera a propósito hasta que exista un sistema de pedidos real.

## Herramientas que requieren aprobación humana

- `generar_reembolso`: requiere aprobación del dueño **siempre**, sin importar el monto. Es la única herramienta que mueve dinero, y el agente no tiene cómo verificar si el reclamo es real (no ve la torta aplastada). Implementado: la herramienta llama a `esperar_aprobacion(...)` (línea 115 de `src/agente.py`) antes de generar nada; si el dueño no responde en 60 segundos, cuenta como **rechazo**. Además, antes de pedir aprobación valida que el monto sea mayor que 0 y no supere el total del pedido ni $50.000.
- Las tres herramientas de riesgo bajo **no** piden aprobación: pedirla para consultar un precio diluiría la atención del dueño, que dejaría de leer las solicitudes que sí importan.

Verificación contra el código (`grep -n "esperar_aprobacion(" src/agente.py`):

```
100:def esperar_aprobacion(mensaje: str) -> bool:
115:    aprobado = esperar_aprobacion(f"Reembolso de ${monto} para el pedido {numero_pedido}.")
```

Probado en `tests/test_agente.py`: un reembolso rechazado no se genera, uno aprobado pide aprobación exactamente una vez, y un monto sobre el total se rechaza sin molestar al dueño.

**Pendiente, declarado tal cual:** hoy la aprobación es por consola (`input` con límite de tiempo). En producción debe ser una notificación al WhatsApp del dueño; la función `aprobador` está separada justamente para reemplazarla sin tocar la herramienta.

## Revisión de trazas

- **Frecuencia:** todos los días, revisando todas las trazas con `generar_reembolso`, y una vez por semana una muestra de 20 trazas de las demás herramientas.
- **Qué se busca**, con ejemplos de las trazas reales:
  - **Herramienta de riesgo alto sin pedido explícito.** En la traza de `cliente_5`, el primer mensaje ("quiero que me devuelvan $10000") **no** disparó el reembolso: el agente pidió confirmación primero y solo lo generó en el segundo turno. Ese es el comportamiento esperado; una traza donde se use al primer mensaje, o sin que el cliente lo pida, se marca.
  - **Respuesta con datos que no vienen de una herramienta.** `cliente_4` ("¿Dónde queda el local?") se respondió sin herramientas, con la dirección del prompt de sistema: correcto. Pero si aparece un precio o un total sin `consultar_precio` o `calcular_total_pedido` en `acciones`, el modelo lo inventó.
  - **Pedido de historial ignorado.** `cliente_2` pidió "el historial completo" y la respuesta final solo dio la hora de entrega, aunque la herramienta devolvió el historial completo. No es peligroso, pero muestra que la respuesta final puede resumir de más.
  - **Fuga entre sesiones.** `cliente_3` preguntó "¿De qué pedido te pregunté recién?" y el agente respondió que no le había dado ningún número: las sesiones no se mezclan. Cualquier traza donde una sesión mencione datos de otra es un incidente grave.
  - **Bucles:** más de 3 acciones en una sola traza (el ejecutor corta en 5 con `max_iterations=5`).
- **Datos personales en las trazas:** a diferencia del servicio RAG (`logs/servicio_rag.log`, que solo guarda longitudes y una huella), `trazas_agente.jsonl` sí guarda la `entrada` completa del cliente, porque sin el texto no se puede auditar por qué el agente eligió una herramienta. Por eso el archivo de trazas en producción debe vivir fuera del repositorio, con acceso solo para el dueño, y borrarse a los 30 días; el que está en el repo tiene solo conversaciones de prueba sin datos reales.
- **Chequeo rápido:** `wc -l trazas_agente.jsonl` y `grep -c '"herramienta": "generar_reembolso"' trazas_agente.jsonl` (hoy: 8 trazas y 1 reembolso).

## Qué hacer ante un comportamiento inesperado

1. **Cortar la herramienta involucrada:** quitarla de `HERRAMIENTAS` en `src/agente.py` y redesplegar. Si es `generar_reembolso`, el agente vuelve a derivar los reclamos al equipo.
2. **Si ya se ejecutó un reembolso indebido:** el dueño lo revierte a mano con el banco y contacta al cliente ese mismo día.
3. **Encontrar la traza** en `trazas_agente.jsonl` (por `session_id` y hora) y anotar qué entrada la provocó, qué herramienta y con qué argumentos.
4. **Reproducir** la entrada en local con `temperature=0`. Si se reproduce, corregir el docstring de la herramienta (para cuándo usarla) o el prompt de sistema, y agregar la entrada como caso en `tests/`.
5. **Reactivar** la herramienta solo cuando la prueba nueva pase, y revisar con más frecuencia (diaria) las trazas de esa herramienta durante la semana siguiente.
