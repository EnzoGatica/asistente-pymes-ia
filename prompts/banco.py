"""Banco de prompts de la miniaplicación: atención de consultas de clientes de pymes."""

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_consulta",
        "system_instruction": (
            "Eres el asistente de atención de una pyme chilena. Clasifica el mensaje del cliente. "
            "Responde únicamente con un JSON con las claves 'categoria' (una de: 'pedido', 'precio', "
            "'horario', 'reclamo', 'otro') y 'urgencia' (entero de 1 a 3, donde 3 es lo más urgente)."
        ),
        "ejemplo_usuario": "Hola, compré un pan amasado ayer y venía crudo por dentro, quiero que me devuelvan la plata.",
        "claves_esperadas": ["categoria", "urgencia"],
        "response_schema": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string", "enum": ["pedido", "precio", "horario", "reclamo", "otro"]},
                "urgencia": {"type": "integer"},
            },
            "required": ["categoria", "urgencia"],
            "additionalProperties": False,
        },
    },
    {
        "nombre": "extraer_datos_pedido",
        "system_instruction": (
            "Extrae los datos del pedido que hace el cliente. Responde únicamente con un JSON con las claves "
            "'producto' (texto), 'cantidad' (entero), 'fecha_entrega' (texto tal como la dijo el cliente, "
            "o cadena vacía) y 'comuna' (texto, o cadena vacía si no la menciona)."
        ),
        "ejemplo_usuario": "Necesito 2 tortas de mil hojas para el sábado 7, con despacho a Dichato porfa.",
        "claves_esperadas": ["producto", "cantidad", "fecha_entrega", "comuna"],
        "response_schema": {
            "type": "object",
            "properties": {
                "producto": {"type": "string"},
                "cantidad": {"type": "integer"},
                "fecha_entrega": {"type": "string"},
                "comuna": {"type": "string"},
            },
            "required": ["producto", "cantidad", "fecha_entrega", "comuna"],
            "additionalProperties": False,
        },
    },
    {
        "nombre": "responder_cliente",
        "system_instruction": (
            "Eres el asistente de una panadería de Tomé que atiende de lunes a sábado de 8:00 a 20:00 y "
            "despacha a Tomé y Dichato. Redacta una respuesta breve (máximo 2 frases), amable y en español "
            "de Chile. Si el cliente pide algo que no puedes confirmar (precios exactos, reembolsos), "
            "marca que requiere atención humana. Responde únicamente con un JSON con las claves "
            "'respuesta' (texto) y 'requiere_humano' (booleano)."
        ),
        "ejemplo_usuario": "¿Hasta qué hora atienden el sábado? ¿Y despachan a Penco?",
        "claves_esperadas": ["respuesta", "requiere_humano"],
        # Sin response_schema a propósito: se valida que el prompt solo baste para obtener JSON.
    },
]
