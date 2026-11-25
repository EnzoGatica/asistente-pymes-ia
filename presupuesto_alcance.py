# Tareas con tecnologia que nunca usaste cuestan mas de lo que parece
FACTOR_NOVEDAD = 1.5
# Horas de laboratorio y evidencia que quedan en el modulo
HORAS_DISPONIBLES = 20
# Parte reservada para pruebas, documentacion y ensayo de la defensa
RESERVA_PRUEBAS_DOCS = 0.30
# Parte reservada para imprevistos
MARGEN_IMPREVISTOS = 0.20
CAPAS_OBLIGATORIAS = {"api", "rag", "contenedor"}

# Lista del asistente de la Panaderia La Espiga (Modulo 3).
# RF-02 y RF-03 reutilizan lo construido en el Modulo 2, por eso no son novedad.
funcionalidades = [
    {"id": "RF-01", "horas": 2, "capa": "api",
     "nombre": "Endpoint POST /consultas con respuesta, fuentes y trace_id",
     "tipo": "imprescindible", "novedad": True, "sistema_real": False},
    {"id": "RF-02", "horas": 1, "capa": "rag",
     "nombre": "Citas de corpus/ desde el indice Chroma persistido",
     "tipo": "imprescindible", "novedad": False, "sistema_real": False},
    {"id": "RF-03", "horas": 1, "capa": "otra",
     "nombre": "Endpoint GET /pedidos/{codigo} con pedidos simulados",
     "tipo": "imprescindible", "novedad": False, "sistema_real": False},
    {"id": "RNF-03", "horas": 2, "capa": "contenedor",
     "nombre": "Contenedor que levanta el servicio con docker compose",
     "tipo": "imprescindible", "novedad": True, "sistema_real": False},
    {"id": "RF-04", "horas": 2, "capa": "otra",
     "nombre": "Aprobacion humana de versiones del prompt expuesta por API",
     "tipo": "deseable", "novedad": False, "sistema_real": False},
    {"id": "RF-05", "horas": 8, "capa": "otra",
     "nombre": "Recepcion directa de mensajes de WhatsApp Business",
     "tipo": "deseable", "novedad": True, "sistema_real": True},
    {"id": "RF-06", "horas": 12, "capa": "otra",
     "nombre": "Panel web con historial de consultas",
     "tipo": "deseable", "novedad": True, "sistema_real": False},
]


def horas_reales(f):
    return f["horas"] * (FACTOR_NOVEDAD if f["novedad"] else 1)


def presupuesto():
    neto = 1 - RESERVA_PRUEBAS_DOCS - MARGEN_IMPREVISTOS
    return round(HORAS_DISPONIBLES * neto, 2)


def recortar(lista):
    limite = presupuesto()
    usado = 0.0
    dentro, fuera = [], []
    orden = sorted(
        lista,
        key=lambda f: (f["tipo"] != "imprescindible", horas_reales(f)),
    )
    for f in orden:
        h = horas_reales(f)
        if f["sistema_real"]:
            fuera.append((f, "requiere datos o sistemas reales"))
        elif usado + h <= limite:
            dentro.append(f)
            usado += h
        else:
            fuera.append((f, "no cabe en el presupuesto"))
    return dentro, fuera, usado


def informe(lista):
    pedido = sum(horas_reales(f) for f in lista)
    dentro, fuera, usado = recortar(lista)
    print(
        f"Pedido: {pedido:.1f} h | Presupuesto: {presupuesto():.1f} h "
        f"({pedido / presupuesto():.1f} veces lo disponible)"
    )
    print(f"\nDENTRO DEL MVP ({usado:.1f} h):")
    for f in dentro:
        print(
            f"  {f['id']} {f['nombre']} [{f['capa']}, {horas_reales(f):.1f} h]"
        )
    print("\nFUERA DE ALCANCE:")
    for f, motivo in fuera:
        print(f"  {f['id']} {f['nombre']} -> {motivo}")
    faltantes = CAPAS_OBLIGATORIAS - {f["capa"] for f in dentro}
    if faltantes:
        print(
            "\nATENCION: capas obligatorias sin cubrir:",
            ", ".join(sorted(faltantes)),
        )
    else:
        print("\nLas tres capas obligatorias estan cubiertas.")


if __name__ == "__main__":
    informe(funcionalidades)
