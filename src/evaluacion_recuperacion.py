"""Evalúa la recuperación con precisión@k y recall@k sobre 12 preguntas etiquetadas a mano.

Los ids relevantes se etiquetaron leyendo corpus/ (salida de partir_en_chunks), antes de correr el retriever.
Uso: python src/evaluacion_recuperacion.py [k]
"""
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from indexar_corpus import CHUNK_OVERLAP, CHUNK_SIZE
from recuperacion import recuperar

RAIZ = Path(__file__).resolve().parent.parent

casos_evaluacion = [
    {"pregunta": "¿A qué hora abren los domingos?", "ids_relevantes": {"horarios.md#1"}},
    {"pregunta": "¿Atienden el 18 de septiembre?", "ids_relevantes": {"horarios.md#2"}},
    {"pregunta": "¿A qué hora sale el pan calentito del horno?", "ids_relevantes": {"horarios.md#2"}},
    {"pregunta": "¿Cuánto vale el kilo de marraqueta?", "ids_relevantes": {"productos_precios.md#1"}},
    {"pregunta": "¿Qué días hay empanadas de mariscos?", "ids_relevantes": {"productos_precios.md#1"}},
    {"pregunta": "¿Cuánto cuesta una torta selva negra para 30 personas?", "ids_relevantes": {"tortas_encargos.md#1"}},
    {"pregunta": "¿Con cuántos días de anticipación encargo una torta para 50 personas?", "ids_relevantes": {"tortas_encargos.md#2"}},
    {"pregunta": "¿Despachan a Penco?", "ids_relevantes": {"despacho.md#1"}},
    {"pregunta": "¿El despacho es gratis si compro mucho?", "ids_relevantes": {"despacho.md#2"}},
    {"pregunta": "¿Me pueden dar factura para mi empresa?", "ids_relevantes": {"medios_pago.md#2"}},
    {"pregunta": "Me llegó el pan en mal estado, ¿qué hago?", "ids_relevantes": {"reclamos_devoluciones.md#1", "reclamos_devoluciones.md#2"}},
    {"pregunta": "¿Tienen pan sin gluten para celíacos?", "ids_relevantes": {"ingredientes_alergenos.md#1"}},
]


def precision_at_k(ids_recuperados, ids_relevantes):
    """Fracción de los ids recuperados que son relevantes (0.0 si no hay ninguno)."""
    if not ids_recuperados:
        return 0.0
    return len([i for i in ids_recuperados if i in ids_relevantes]) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Fracción de los ids relevantes que se recuperaron (None si el caso no tiene ninguno)."""
    if not ids_relevantes:
        return None
    return len([i for i in ids_recuperados if i in ids_relevantes]) / len(ids_relevantes)


def promediar(valores):
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(recuperar_fn, casos, k=3):
    resultados = []
    for caso in casos:
        ids_recuperados = [c.id for c in recuperar_fn(caso["pregunta"], k)][:k]
        resultados.append({
            "pregunta": caso["pregunta"],
            "ids_recuperados": ids_recuperados,
            "precision": precision_at_k(ids_recuperados, caso["ids_relevantes"]),
            "recall": recall_at_k(ids_recuperados, caso["ids_relevantes"]),
        })
    return resultados, promediar(r["precision"] for r in resultados), promediar(r["recall"] for r in resultados)


def formatear_resultados(resultados, precision_promedio, recall_promedio, k):
    lineas = [f"Fecha: {date.today()}", f"Configuracion: k={k}, chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}, "
              "embeddings=text-embedding-3-small", ""]
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        lineas.append(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}  ->  {', '.join(r['ids_recuperados'])}")
    lineas.append(f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}")
    return "\n".join(lineas)


if __name__ == "__main__":
    load_dotenv()
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(recuperar, casos_evaluacion, k=K)
    texto = formatear_resultados(resultados, precision_promedio, recall_promedio, K)
    print(texto)
    archivo = RAIZ / ("resultados_evaluacion.txt" if K == 3 else f"resultados_evaluacion_k{K}.txt")
    archivo.write_text(texto + "\n", encoding="utf-8")
    print(f"Resultados guardados en {archivo.name}")
