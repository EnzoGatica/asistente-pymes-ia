# Asistente de consultas para pymes

Asistente de IA generativa para atender los mensajes que los clientes de una pyme (en el ejemplo, una panadería de Tomé) mandan por WhatsApp o Instagram.

- **Gate 1 (`main.py`):** clasifica el mensaje (pedido, precio, horario, reclamo u otro, con urgencia de 1 a 3) y propone una respuesta breve, indicando si requiere atención humana. Usa prompts de sistema y salida JSON validada.
- **Gate 2 (`servicio_rag.py`):** responde con los datos reales del negocio mediante RAG sobre `corpus/`, cita la fuente de cada respuesta, filtra intentos de inyección, deja trazas JSON sin datos personales y exige aprobación humana para desplegar una versión nueva del prompt.

Modelo: OpenAI `gpt-4.1-nano` (ver [decisión de modelo](docs/decision-arquitectura.md)); embeddings `text-embedding-3-small`; vector store Chroma; orquestación con LangChain y LangGraph.

Proyecto de la Especialización en Desarrollo con IA Generativa (Accenture · Skillnest), construido bloque a bloque sobre la plantilla base del programa.

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- Git
- Una llave de API de OpenAI ([crear una aquí](https://platform.openai.com/api-keys))

## Instalación

**Windows (PowerShell)**

```powershell
git clone https://github.com/EnzoGatica/asistente-pymes-ia.git
cd asistente-pymes-ia
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

**macOS / Linux / WSL**

```bash
git clone https://github.com/EnzoGatica/asistente-pymes-ia.git
cd asistente-pymes-ia
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Luego abre el archivo `.env` y reemplaza `tu_llave_aqui` por tu llave real:

```
OPENAI_API_KEY=sk-...
```

El `.env` está en `.gitignore`: nunca se sube al repositorio. Para comprobar que todo quedó bien: `python verificar_entorno.py` (no imprime la llave).

## Ejecución

Con el entorno virtual activo, desde la raíz del proyecto (en macOS/Linux usa `python3`).

### Gate 1: clasificar y proponer respuesta

```bash
python main.py "Hola, ¿tienen marraquetas calientes? ¿Cuánto sale el kilo?"
```

Si no pasas el mensaje como argumento, el programa lo pide por consola. Salida esperada (el texto varía porque lo genera el modelo):

```
Categoría: precio (urgencia 2/3)
Respuesta del modelo: ¡Hola! Tenemos marraquetas en el día, pero el precio del kilo requiere atención humana.
Requiere atención humana: sí
Costo total: USD 0.0000516
Proceso terminado sin errores.
```

Si algo falla (llave inválida, sin conexión, mensaje vacío), el programa muestra `No se pudo completar la operación: <motivo>` en vez de un traceback.

### Gate 2: servicio RAG con fuentes citadas

```bash
python servicio_rag.py
```

Sin argumentos corre dos consultas de ejemplo y después el **punto de supervisión humana**: el despliegue de la versión nueva del prompt se pausa y pregunta `¿Aprobar? (s/n)`. Para una consulta puntual (sin el paso de supervisión):

```bash
python servicio_rag.py "¿Despachan a Penco?"
```

La primera corrida crea el índice en `vectorstore/` a partir de `corpus/` (unos segundos). Las siguientes lo reutilizan y solo reindexan los chunks que cambiaron (`indice_reutilizado` / `indice_actualizado` en el log). Para reconstruirlo desde cero: `python src/indexar_corpus.py`.

Salida esperada (resumida; los logs JSON salen por consola y en `logs/servicio_rag.log`):

```
{"msg": "consulta_recibida", "trace_id": "trace-b2667016", "pregunta_len": 54, "pregunta_huella": "9f8dbca3"}
{"msg": "documentos_recuperados", "trace_id": "trace-b2667016", "n": 3, "fuentes": ["despacho.md", ...]}
{"msg": "consumo_llm", "trace_id": "trace-b2667016", "input_tokens": 415, "output_tokens": 19, "costo_usd": 4.91e-05}
Respuesta final: No, no despachamos a Penco. Puedes retirar en nuestro local si prefieres. [Fuentes: despacho.md, ...]
Punto de supervisión: aprobar nueva version de prompt en produccion (actual 849809fdf663 -> propuesta 63e87a2e20b7)
¿Aprobar? (s/n): s
version 63e87a2e20b7 activada
Proceso terminado sin errores.
```

### Pruebas

```bash
python -m pytest -v
```

70 pruebas, sin llamar a la API (todo con mocks, embeddings deterministas y modelo simulado). `tests/test_gate2.py` verifica los cuatro criterios no compensables del Gate 2.

### Scripts por bloque

| Comando | Bloque | Qué hace |
|---|---|---|
| `python src/consumir_openai.py` | 5-8 | Prueba mínima de conexión: una pregunta y su costo |
| `python src/comparar_modelos.py` | 9 | Latencia y costo de `gpt-4.1-nano` vs `gpt-4.1-mini` |
| `python prompts/test_consistencia.py` | 10 | Corre cada prompt del banco 3 veces y guarda el registro |
| `python src/cliente.py` | 12-13 | Cliente modular con reintento, backoff y registro de costo |
| `python src/comparar_crudo_vs_procesado.py` | 15 | Coincidencia antes y después del pipeline de texto |
| `python src/evaluar_salidas.py` | 16-17 | 20 respuestas reales con precisión, cobertura y F1 |
| `python src/cadena_tres_pasos.py` | 18 | Chain clasificar → redactar → revisar tono |
| `python src/enrutamiento.py` | 19-20 | Chain con enrutamiento por categoría y fallbacks |
| `python src/agente.py` | 21-23 | Agente con 4 herramientas, memoria por sesión y aprobación de reembolsos |
| `python src/indexar_corpus.py` | 24 | Indexa `corpus/` en Chroma desde cero |
| `python src/recuperacion.py` | 26 | Recuperación con prompt dinámico y citas |
| `python src/evaluacion_recuperacion.py [k]` | 27 | Precisión@k y recall@k sobre 12 preguntas etiquetadas |
| `python src/registro_rag.py` | 28 | Latencia por etapa, tokens y costo del flujo RAG |
| `python src/dataset_tuning.py` | 29 | Dataset validado para PEFT (no lo envía a entrenar) |
| `python decision.py` | 30 | Método de decisión RAG / fine-tuning / PEFT |
| `python src/logging_rag.py` | 31 | Demo de logging con trace_id y filtro de inyección |
| `python src/registro_prompts.py` | 32 | Versiones del prompt con huella y diff |
| `python src/grafo_supervision.py` | 32 | Punto de supervisión: aprobación y rechazo |
| `python src/matriz_riesgos.py` | 32 | Matriz de riesgos con puntaje y supervisión |
| `python rubrica_gate2.py` | Gate 2 | Autoevaluación contra la rúbrica |

## Estructura

```
main.py                    Gate 1: clasifica y propone respuesta
servicio_rag.py            Gate 2: servicio RAG integrado (índice incremental, citas, trazas, supervisión)
corpus/                    8 documentos del negocio de ejemplo (fuente del RAG)
src/consumir_openai.py     armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json, calcular_costo
src/cliente.py             Cliente modular: consultar_modelo con reintento, backoff y registro de costo
src/pipeline_texto.py      Limpieza, tokenización y métricas de precisión/cobertura/F1
src/cadena_tres_pasos.py, src/enrutamiento.py   Orquestación con LangChain
src/agente.py              Agente con herramientas, memoria, aprobación humana y trazas
src/indexar_corpus.py, src/recuperacion.py, src/evaluacion_recuperacion.py, src/registro_rag.py   RAG
src/logging_rag.py         Logging JSON con trace_id, consumo y filtro de inyección
src/registro_prompts.py, src/grafo_supervision.py, src/matriz_riesgos.py   Gobernanza
prompts/                   Banco de prompts, consistencia y registro de versiones
tests/                     70 pruebas con pytest
docs/                      Diagramas, decisiones, límites y evidencias de cada bloque
vectorstore/, logs/        Generados al correr (fuera de Git)
```

## Documentación

- [Diagrama de arquitectura](docs/diagrama_arquitectura.png) y [decisión de modelo](docs/decision-arquitectura.md)
- [Límites de la métrica de evaluación](docs/limites_metrica.md)
- [Límites de autonomía del agente](docs/limites_autonomia_agente.md)
- [Decisión de personalización](decision_personalizacion.md)
- [Evaluación de la recuperación](resultados_evaluacion.txt) y [registros de latencia y costo](registros_latencia_costo.jsonl)
- [Matriz de riesgos y supervisión](docs/evidencia_gobernanza.txt)

## Registro del ensayo de instalación limpia (Gate 1)

- Fecha: 2026-10-22
- Procedimiento: `git clone` del remoto en una carpeta nueva, entorno virtual nuevo, `pip install -r requirements.txt`, `.env` creado desde `.env.example`, `python main.py` siguiendo solo este README.
- Entorno: Windows 11, Python 3.14, PowerShell/Git Bash.
- Encontrado: sin hallazgos. `requirements.txt` completo, `.env.example` presente, `main.py` terminó sin traceback ("Proceso terminado sin errores.").
- Seguridad: en la copia clonada `git status` no lista `.env`, `git ls-files` solo muestra `.env.example` y `git log --all -- .env` no devuelve commits.
