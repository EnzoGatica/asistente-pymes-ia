# Plan de pruebas parciales

Cada componente del flujo de una consulta se prueba solo, sin red, sin Docker y sin leer el entorno real. La columna "Defecto introducido" es el cambio que se aplicó en una copia con `verificar_defectos.py` para comprobar que la prueba lo detecta.

| Componente | Entrada | Salida | Doble | Archivo | Defecto introducido | Detectado |
|---|---|---|---|---|---|---|
| formatear_contexto | lista de Document recuperados | texto "[fuente] contenido" por fragmento | Document escritos a mano | tests/parciales/test_contexto.py | se pierde la etiqueta [fuente] del fragmento | sí |
| asegurar_cita | texto del modelo y fuentes usadas | texto que cita al menos una fuente usada | ninguno: textos escritos a mano | tests/parciales/test_citas.py | la condición queda en "if True:" y nunca agrega fuentes | sí |
| detección sin cobertura | texto del modelo | coincidencia o None | ninguno: textos escritos a mano | tests/parciales/test_sin_cobertura.py | la expresión deja de reconocer "contamos" y "dispongo" | sí |
| filtro de inyección | lista de Document recuperados | (limpios, descartados con patrones) | Document con un ataque escrito a mano | tests/parciales/test_inyeccion.py | el filtro deja pasar todo ("if False:") | sí |
| estado de pedidos | código de pedido | dict del pedido o PedidoNoEncontrado | ninguno: datos simulados de src/negocio.py | tests/parciales/test_pedidos.py | un pedido inexistente devuelve {} en vez de fallar | sí |

## Cómo repetir cada defecto

```
python verificar_defectos.py servicio_rag.py "f\"[{d.metadata['fuente']}] {d.page_content}\"" "d.page_content" tests/parciales/test_contexto.py
python verificar_defectos.py servicio_rag.py "if citadas & set(fuentes):" "if True:" tests/parciales/test_citas.py
python verificar_defectos.py servicio_rag.py "(?:tengo|tenemos|cuento|contamos|dispongo|disponemos)" "(?:tengo|tenemos)" tests/parciales/test_sin_cobertura.py
python verificar_defectos.py src/logging_rag.py "        if coincidencias:" "        if False:" tests/parciales/test_inyeccion.py
python verificar_defectos.py servicio/logica.py "raise PedidoNoEncontrado(codigo)" "return {}" tests/parciales/test_pedidos.py
```

Las cinco líneas terminan en `DETECTADO` (código de salida 0). La integración de los componentes se prueba aparte en `tests/test_api.py` y `tests/test_gate2.py`.
