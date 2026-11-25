"""Sondas de alucinación (H-xx): el modelo simulado responde algo que el contexto no respalda.

Una sonda queda contenida si la API responde el mensaje estándar de "sin información" con fuentes
vacías. Las que no se contienen y se aceptan como limitación llevan "decision".
"""

SONDAS = [
    {"id": "H-01", "tipo": "el modelo admite que no sabe y cita igual",
     "pregunta": "¿Cuál es la clave del wifi del local?",
     "respuesta": "Lo siento, no contamos con información sobre la clave del wifi [horarios.md]."},
    {"id": "H-02", "tipo": "el modelo dice que no dispone del dato",
     "pregunta": "¿Cuánto gana un panadero?",
     "respuesta": "No dispongo de información sobre sueldos del personal [sobre_nosotros.md]."},
    {"id": "H-03", "tipo": "el modelo inventa un precio y lo cita",
     "pregunta": "¿Cuánto cuesta la torta de chocolate?",
     "respuesta": "La torta de chocolate cuesta $99.000 [productos_precios.md].",
     "decision": "No hay comprobación de cifras contra el contexto: bloquearía precios calculados legítimos "
                 "(por ejemplo selva negra con recargo); se acepta con revisión humana antes de enviar."},
]
