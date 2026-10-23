"""Método de decisión de personalización (Bloque 30) aplicado al asistente de la panadería.

Uso: python decision.py  -> escribe el esqueleto en decision_personalizacion_esqueleto.md
(el documento final, completado a mano, es decision_personalizacion.md).
"""


def recomendar_estrategia(respuestas):
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}
    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2
    maximo = max(puntos.values())
    return puntos, [tecnica for tecnica, p in puntos.items() if p == maximo]


respuestas_mi_caso = {
    # corpus/productos_precios.md: "los precios se actualizan el primer día hábil de cada mes"; además
    # horarios de feriados, despachos y productos de temporada cambian varias veces al año.
    "informacion_cambia_seguido": True,
    # resultados_metricas.json: de 20 respuestas reales, 2 (10 %) fallan el tono (tercera persona:
    # "Abren a las 8:00", "Cobran $2.000"), 0 superan 2 frases; el JSON con json_schema dio 9/9 válidos
    # (prompts/registro_resultados.json). 10 % < umbral de 15 %.
    "problema_de_formato_o_tono": False,
    # datos/dataset_tuning.jsonl tiene 17 ejemplos etiquetados: lejos de 200.
    "dataset_grande_y_de_calidad": False,
    # El cliente es una pyme: no se pagan entrenamientos, y un cambio de precio debe verse el mismo día.
    "presupuesto_limitado_o_iterar_rapido": True,
    # Un solo comportamiento (atender clientes en español de Chile); lo que cambia entre negocios es la
    # información, que se resuelve con un corpus por negocio, no con un modelo por negocio.
    "necesita_multiples_variantes": False,
}


def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = ["# Decision de personalizacion", "", "## 1. El problema", problema, "", "## 2. Resultado del metodo de decision"]
    lineas += [f"- {tecnica}: {p} puntos" for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1])]
    if empate:
        lineas += ["", f"**Empate entre: {', '.join(ganadoras)}**"]
    lineas += ["", "## 3. Tecnica elegida y por que"]
    lineas.append("[COMPLETAR: el puntaje no resolvio el empate solo -- justifica aqui con criterio propio]" if empate
                  else f"[COMPLETAR: por que {ganadoras[0]} responde mejor a este caso]")
    lineas += ["", "## 4. Que necesitarias para ejecutarla", "[COMPLETAR: corpus faltante, o cantidad de ejemplos etiquetados que faltan]"]
    return "\n".join(lineas)


if __name__ == "__main__":
    if any(valor is None for valor in respuestas_mi_caso.values()):
        raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")
    puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
    print(puntos)
    print("candidatas:", ganadoras)
    variante = dict(respuestas_mi_caso, problema_de_formato_o_tono=True)
    print("si el tono fallara en 15 % o más:", recomendar_estrategia(variante)[0])
    esqueleto = generar_esqueleto_decision(
        "El asistente necesita responder con los datos vigentes de cada pyme (precios, horarios, despacho).",
        puntos, ganadoras,
    )
    with open("decision_personalizacion_esqueleto.md", "w", encoding="utf-8") as f:
        f.write(esqueleto + "\n")
    print(esqueleto)
