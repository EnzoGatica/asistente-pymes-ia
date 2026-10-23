"""Ficha del negocio de ejemplo que usa el asistente (datos ficticios)."""

FICHA_NEGOCIO = """Panadería La Espiga, calle Egaña 1450, Tomé, Región del Biobío.
Horario: lunes a sábado de 8:00 a 20:00; domingo de 9:00 a 14:00.
Productos y precios: marraqueta $2.200 el kilo, hallulla $2.400 el kilo, pan amasado $600 la unidad,
empanada de pino $2.500, torta de mil hojas para 15 personas $22.000, para 30 personas $38.000.
Las tortas se encargan con 48 horas de anticipación.
Despacho a domicilio en Tomé ($2.000) y Dichato ($3.500); no despachamos a otras comunas.
Medios de pago: efectivo, débito, crédito y transferencia. Emitimos boleta electrónica.
Contacto: WhatsApp +56 9 1234 5678."""

SISTEMA_ASISTENTE = (
    "Eres el asistente de atención al cliente de esta panadería. Responde en una o dos frases, en español "
    "de Chile, usando solo la información de la ficha. Si la ficha no tiene el dato, dilo.\n\n" + FICHA_NEGOCIO
)

# Los mismos datos de la ficha, en forma estructurada para las herramientas del agente.
PRECIOS = {
    "marraqueta": (2200, "kilo"),
    "hallulla": (2400, "kilo"),
    "pan amasado": (600, "unidad"),
    "empanada de pino": (2500, "unidad"),
    "torta 15 personas": (22000, "unidad"),
    "torta 30 personas": (38000, "unidad"),
}
DESPACHO = {"tome": 2000, "dichato": 3500}

PEDIDOS = {
    "P-1001": {"estado": "en preparación", "total": 6800,
               "historial": ["recibido 21-10 18:05", "pagado por transferencia 21-10 18:20", "en preparación 22-10 07:30"]},
    "P-1002": {"estado": "entregado", "total": 41500,
               "historial": ["recibido 19-10 10:12", "pagado 19-10 10:40", "despachado a Dichato 21-10 15:00", "entregado 21-10 16:10"]},
}
