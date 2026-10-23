"""Revisión manual de 10 casos de resultados_metricas.json (5 de F1 más bajo y 5 de F1 = 1.0).

Rúbrica del Bloque 17: corrección factual, completitud y contradicción (si / no / parcial).
Ejecutar con: python revision_manual.py  (genera revision_manual.json)
"""
import json

revision_manual = [
    # --- F1 más bajo ---
    {
        "consulta": "¿A qué hora abren el lunes?",
        "f1": 0.43,
        "correccion_factual": "si",
        "completitud": "parcial",
        "contradiccion": "no",
        "nota": "Dice 8:00 (correcto) pero omite la hora de cierre que sí está en la referencia; "
                "además habla en tercera persona ('Abren') en vez de la voz del negocio.",
    },
    {
        "consulta": "¿Puedo pagar con tarjeta de crédito?",
        "f1": 0.43,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Respuesta correcta y suficiente para lo que se preguntó; el F1 baja solo porque la "
                "referencia enumera todos los medios de pago. Falso negativo de la métrica.",
    },
    {
        "consulta": "¿Tienen estacionamiento?",
        "f1": 0.55,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Reconoce que no tiene el dato, que es lo correcto (la ficha no lo menciona). "
                "La métrica castiga la paráfrasis 'no tengo esa información'.",
    },
    {
        "consulta": "¿Venden pan sin gluten?",
        "f1": 0.57,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "No inventa productos: dice que no tiene información. Correcto; F1 bajo por redacción distinta.",
    },
    {
        "consulta": "¿Aceptan transferencia?",
        "f1": 0.6,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Agrega 'como medio de pago': palabras extra correctas que bajan la precisión.",
    },
    # --- F1 = 1.0 ---
    {
        "consulta": "¿Cuánto vale el kilo de marraqueta?",
        "f1": 1.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Idéntica a la referencia. Ojo: el precio '$2.200' se tokeniza como '2' y '200'; "
                "si el modelo dijera '$2.000' igual compartiría el token '2'.",
    },
    {
        "consulta": "¿Precio de la hallulla?",
        "f1": 1.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Correcta. El 1.0 aquí sí coincide con una respuesta perfecta.",
    },
    {
        "consulta": "¿Cuánto cuesta la torta para 15 personas?",
        "f1": 1.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Correcta, pero no menciona la anticipación de 48 h, que al cliente le serviría saber. "
                "La métrica no puede premiar información útil que no esté en la referencia.",
    },
    {
        "consulta": "¿Con cuánta anticipación encargo una torta?",
        "f1": 1.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Copia literal de la ficha del negocio: el F1 perfecto refleja que el modelo citó la fuente.",
    },
    {
        "consulta": "¿Dan boleta?",
        "f1": 1.0,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "Correcta y breve.",
    },
]

if __name__ == "__main__":
    with open("revision_manual.json", "w", encoding="utf-8") as archivo:
        json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)
    print(f"{len(revision_manual)} casos revisados guardados en revision_manual.json")
