# Limitaciones conocidas

Lo que el asistente no hace, dónde se descubrió y qué se decidió. Cada fila apunta a la evidencia ejecutable, al riesgo de docs/matriz_riesgos.md que la cubre y a la decisión de docs/decisiones.md que la explica.

| ID | Qué no hace | Origen | Riesgo | Efecto | Qué se decidió |
|---|---|---|---|---|---|
| LIM-01 | No reconoce una orden escondida en un fragmento si está redactada con otras palabras ("deja de lado tus reglas"). | ataques:A-03 | R-01 | El fragmento llega al modelo como contexto; el prompt v2 lo trata como datos, pero no hay garantía. | Declarada: el filtro lee patrones; se amplían con cada caso nuevo y la dueña revisa la respuesta antes de enviarla (D-06). |
| LIM-02 | No detecta un precio o dato inventado si el modelo lo cita con una fuente real. | alucinaciones:H-03 | R-02 | El cliente podría recibir un precio que no está en corpus/, con apariencia de respaldado. | Declarada: comparar cifras bloquearía precios calculados legítimos; la dueña revisa precios y plazos antes de enviar (D-04). |

Otros límites de alcance, sin evidencia en el código: los datos del negocio y los pedidos son simulados, no hay conexión con WhatsApp y no se probó con varios usuarios a la vez (ver docs/registro_ejecucion.md).
