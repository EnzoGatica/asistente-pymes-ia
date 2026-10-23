"""Genera 20 respuestas reales con consultar_modelo y calcula sus métricas contra una referencia propia."""
import json
from pathlib import Path

from cliente import consultar_modelo
from negocio import SISTEMA_ASISTENTE
from pipeline_texto import calcular_metricas, resumir_metricas

SALIDA = Path(__file__).resolve().parent.parent / "resultados_metricas.json"

CASOS = [
    ("¿A qué hora abren el lunes?", "El lunes abrimos a las 8:00 y cerramos a las 20:00."),
    ("¿Atienden el domingo?", "Sí, el domingo atendemos de 9:00 a 14:00."),
    ("¿Cuánto vale el kilo de marraqueta?", "El kilo de marraqueta cuesta $2.200."),
    ("¿Precio de la hallulla?", "La hallulla cuesta $2.400 el kilo."),
    ("¿Cuánto sale un pan amasado?", "El pan amasado cuesta $600 la unidad."),
    ("¿Tienen empanadas de pino? ¿A cuánto?", "Sí, la empanada de pino cuesta $2.500."),
    ("Quiero una torta para 30 personas, ¿cuánto sale?", "La torta de mil hojas para 30 personas cuesta $38.000."),
    ("¿Cuánto cuesta la torta para 15 personas?", "La torta de mil hojas para 15 personas cuesta $22.000."),
    ("¿Con cuánta anticipación encargo una torta?", "Las tortas se encargan con 48 horas de anticipación."),
    ("¿Despachan a Dichato?", "Sí, despachamos a Dichato por $3.500."),
    ("¿Cuánto cobran por despacho dentro de Tomé?", "El despacho en Tomé cuesta $2.000."),
    ("¿Hacen despacho a Penco?", "No, solo despachamos a Tomé y Dichato."),
    ("¿Puedo pagar con tarjeta de crédito?", "Sí, aceptamos efectivo, débito, crédito y transferencia."),
    ("¿Aceptan transferencia?", "Sí, aceptamos transferencia."),
    ("¿Dan boleta?", "Sí, emitimos boleta electrónica."),
    ("¿Dónde están ubicados?", "Estamos en calle Egaña 1450, Tomé."),
    ("¿Cuál es su WhatsApp?", "Nuestro WhatsApp es +56 9 1234 5678."),
    ("¿Venden pan sin gluten?", "La ficha no tiene información sobre pan sin gluten."),
    ("¿Hasta qué hora atienden el sábado?", "El sábado atendemos hasta las 20:00."),
    ("¿Tienen estacionamiento?", "No tengo información sobre estacionamiento."),
]

if __name__ == "__main__":
    resultados = []
    for consulta, referencia in CASOS:
        respuesta = consultar_modelo(consulta, SISTEMA_ASISTENTE)
        resultados.append({"consulta": consulta, "referencia": referencia, "respuesta": respuesta,
                           **calcular_metricas(referencia, respuesta)})
        SALIDA.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")  # guarda en cada vuelta
    print("Resumen:", resumir_metricas(resultados))
    print("Peores casos:")
    for caso in sorted(resultados, key=lambda r: r["f1"])[:3]:
        print(f"  {caso['consulta']} f1={caso['f1']}")
