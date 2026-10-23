"""Dataset para personalizar (PEFT / fine-tuning) la clasificación de mensajes de clientes.

Problema de comportamiento, no de conocimiento: el modelo debe devolver SIEMPRE el mismo JSON
{"categoria", "urgencia"} con categorías fijas. Formato de salida: JSONL de chat de OpenAI
(un {"messages": [system, user, assistant]} por línea), el que acepta su API de fine-tuning.
Uso: python src/dataset_tuning.py  (valida y escribe datos/dataset_tuning.jsonl; no envía nada a entrenar)
"""
import json
from collections import Counter
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "datos" / "dataset_tuning.jsonl"
SISTEMA = "Clasifica el mensaje de un cliente de panadería. Responde solo con JSON: categoria y urgencia (1 a 3)."
CATEGORIAS = {"pedido", "precio", "horario", "reclamo", "otro"}
CLAVES_ESPERADAS = ("categoria", "urgencia")

ejemplos_raw = [
    ("Necesito 2 tortas de mil hojas para el sábado con despacho a Dichato.", {"categoria": "pedido", "urgencia": 2}),
    ("Quiero encargar 50 empanadas de pino para mañana a las 12, es para un velorio.", {"categoria": "pedido", "urgencia": 3}),
    ("¿Me pueden guardar 3 kilos de marraqueta para las 7 de la tarde?", {"categoria": "pedido", "urgencia": 2}),
    ("Para el próximo mes quiero cotizar una torta para 50 personas.", {"categoria": "pedido", "urgencia": 1}),
    ("¿A cuánto está el kilo de hallulla?", {"categoria": "precio", "urgencia": 1}),
    ("¿Cuánto sale la torta selva negra para 30?", {"categoria": "precio", "urgencia": 1}),
    ("hola cuanto cobran el despacho a dichato", {"categoria": "precio", "urgencia": 1}),
    ("¿Abren el 1 de mayo?", {"categoria": "horario", "urgencia": 1}),
    ("Voy saliendo, ¿alcanzo a llegar antes de que cierren hoy domingo?", {"categoria": "horario", "urgencia": 2}),
    ("¿A qué hora sale el pan calentito?", {"categoria": "horario", "urgencia": 1}),
    ("El pan amasado de hoy venía crudo por dentro, quiero que me devuelvan la plata.", {"categoria": "reclamo", "urgencia": 3}),
    ("La torta llegó aplastada y el cumpleaños es en una hora!!", {"categoria": "reclamo", "urgencia": 3}),
    ("Ayer me cobraron dos veces con la tarjeta.", {"categoria": "reclamo", "urgencia": 2}),
    ("El despacho llegó 40 minutos tarde, ojalá no se repita.", {"categoria": "reclamo", "urgencia": 1}),
    ("¿Están contratando panaderos?", {"categoria": "otro", "urgencia": 1}),
    ("Felicitaciones por las empanadas de la Fiesta de la Chilenidad, estaban buenísimas.", {"categoria": "otro", "urgencia": 1}),
    ("¿Tienen pan sin gluten? Mi hijo es celíaco.", {"categoria": "otro", "urgencia": 2}),
]


def a_formato_chat(texto, salida):
    return {"messages": [
        {"role": "system", "content": SISTEMA},
        {"role": "user", "content": texto},
        {"role": "assistant", "content": json.dumps(salida, ensure_ascii=False)},
    ]}


def chequear_balance(ejemplos: list[tuple[str, dict]], clave: str) -> Counter:
    return Counter(salida[clave] for _, salida in ejemplos)


def validar_dataset(ejemplos: list[dict], claves_esperadas: tuple[str, ...] = CLAVES_ESPERADAS) -> list[str]:
    problemas = []
    vistos = set()
    for i, ejemplo in enumerate(ejemplos):
        mensajes = ejemplo.get("messages", [])
        if [m.get("role") for m in mensajes] != ["system", "user", "assistant"]:
            problemas.append(f"ejemplo {i}: los roles deben ser system, user, assistant")
            continue
        entrada, salida_texto = mensajes[1]["content"], mensajes[2]["content"]
        if not entrada or not entrada.strip():
            problemas.append(f"ejemplo {i}: mensaje de usuario vacío")
        if entrada in vistos:
            problemas.append(f"ejemplo {i}: mensaje de usuario duplicado")
        vistos.add(entrada)
        try:
            salida = json.loads(salida_texto)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: la salida no es JSON válido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: la salida no tiene la clave "{clave}"')
        if salida.get("categoria") not in CATEGORIAS:
            problemas.append(f"ejemplo {i}: categoría desconocida {salida.get('categoria')!r}")
        if salida.get("urgencia") not in (1, 2, 3):
            problemas.append(f"ejemplo {i}: urgencia fuera de rango {salida.get('urgencia')!r}")
    return problemas


if __name__ == "__main__":
    ejemplos = [a_formato_chat(texto, salida) for texto, salida in ejemplos_raw]
    print(f"{len(ejemplos)} ejemplos construidos")
    print("Balance por categoría:")
    for categoria, cuenta in chequear_balance(ejemplos_raw, "categoria").most_common():
        print(f"  {categoria}: {cuenta}")
    print("Balance por urgencia:", dict(sorted(chequear_balance(ejemplos_raw, "urgencia").items())))

    problemas = validar_dataset(ejemplos)
    print(f"{len(ejemplos)} ejemplos, {len(problemas)} problemas encontrados")

    roto = json.loads(json.dumps(ejemplos[:2])) + [ejemplos[0]]  # copia con un duplicado
    roto[1]["messages"][2]["content"] = "{'categoria': 'precio'}"  # comillas simples, sin urgencia
    print("Prueba del validador con un dataset roto a propósito:")
    for problema in validar_dataset(roto):
        print("  -", problema)

    if problemas:
        raise SystemExit("Corrige los problemas antes de escribir el dataset.")
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in ejemplos) + "\n", encoding="utf-8")
    print(f"Dataset escrito en {SALIDA.relative_to(SALIDA.parent.parent)}")
