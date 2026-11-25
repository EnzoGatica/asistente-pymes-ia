# Registro de alucinaciones

Fecha: 2026-11-25
Cada sonda hace que el modelo simulado responda algo que el contexto no respalda; contenida significa que la API devolvió el mensaje de sin información con fuentes vacías.

| Sonda | Tipo | Resultado | Decisión |
|---|---|---|---|
| H-01 | el modelo admite que no sabe y cita igual | PASA |  |
| H-02 | el modelo dice que no dispone del dato | PASA |  |
| H-03 | el modelo inventa un precio y lo cita | LIMITE | No hay comprobación de cifras contra el contexto: bloquearía precios calculados legítimos (por ejemplo selva negra con recargo); se acepta con revisión humana antes de enviar. |
