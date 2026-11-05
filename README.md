# Asistente de consultas para pymes

Asistente de IA generativa para atender los mensajes que los clientes de una pyme (en el ejemplo, una panadería de Tomé) mandan por WhatsApp o Instagram.

- **Gate 1 (`main.py`):** clasifica el mensaje (pedido, precio, horario, reclamo u otro, con urgencia de 1 a 3) y propone una respuesta breve, indicando si requiere atención humana. Usa prompts de sistema y salida JSON validada.
- **Gate 2 (`servicio_rag.py`):** responde con los datos reales del negocio mediante RAG sobre `corpus/`, cita la fuente de cada respuesta, filtra intentos de inyección, deja trazas JSON sin datos personales y exige aprobación humana para desplegar una versión nueva del prompt.

Modelo: OpenAI `gpt-4.1-nano` (ver [decisión de modelo](docs/decision-arquitectura.md)); embeddings `text-embedding-3-small`; vector store Chroma; orquestación con LangChain y LangGraph.

Proyecto de la Especialización en Desarrollo con IA Generativa (Accenture · Skillnest), construido bloque a bloque sobre la plantilla base del programa.

## Entregas por bloque

Cada actividad, con el archivo que la responde y el commit en que se entregó.

| Bloque | Actividad | Archivo entregado | Commit |
|---|---|---|---|
| 2 | Inicializa tu repositorio y primer commit | [`.gitignore`](.gitignore), [`.env.example`](.env.example) | [b3c3f32](https://github.com/EnzoGatica/asistente-pymes-ia/commit/b3c3f32) |
| 3 | Réplica del setup completo | [`requirements.txt`](requirements.txt) | [844f90d](https://github.com/EnzoGatica/asistente-pymes-ia/commit/844f90d) |
| 4 | Primera petición autenticada | [`docs/evidencia_peticion_autenticada.txt`](docs/evidencia_peticion_autenticada.txt), [colección de Postman](docs/primera_peticion.postman_collection.json) y [su ejecución](docs/evidencia_peticion_postman.txt) | [e546b25](https://github.com/EnzoGatica/asistente-pymes-ia/commit/e546b25) |
| 5 | Módulo Python de consumo de servicios | [`src/consumir_openai.py`](src/consumir_openai.py) | [e88c8f1](https://github.com/EnzoGatica/asistente-pymes-ia/commit/e88c8f1) |
| 6 | Script refactorizado en funciones | [`src/consumir_openai.py`](src/consumir_openai.py) | [c4ab1b9](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c4ab1b9) |
| 7 | Excepciones y validación | [`docs/evidencia_manejo_errores.txt`](docs/evidencia_manejo_errores.txt) | [ebd0443](https://github.com/EnzoGatica/asistente-pymes-ia/commit/ebd0443) |
| 8 | Diagrama de arquitectura | [`docs/diagrama_arquitectura.png`](docs/diagrama_arquitectura.png) | [c3f9c9e](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c3f9c9e) |
| 9 | Decisión de arquitectura (elección de modelo) | [`docs/decision-arquitectura.md`](docs/decision-arquitectura.md), [`src/comparar_modelos.py`](src/comparar_modelos.py) | [8553030](https://github.com/EnzoGatica/asistente-pymes-ia/commit/8553030) |
| 10 | Banco de prompts y consistencia | [`prompts/banco.py`](prompts/banco.py), [`prompts/registro_resultados.json`](prompts/registro_resultados.json) | [0fdd4de](https://github.com/EnzoGatica/asistente-pymes-ia/commit/0fdd4de) |
| 11 | **Gate 1** - Habilitación técnica | [`main.py`](main.py), este README | [1e9a02f](https://github.com/EnzoGatica/asistente-pymes-ia/commit/1e9a02f) |
| 12 | Cliente modular con reintentos | [`src/cliente.py`](src/cliente.py), [`docs/evidencia_cliente_modular.txt`](docs/evidencia_cliente_modular.txt) | [c27d200](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c27d200) |
| 13 | Rate limits, backoff y costo por operación | [`docs/evidencia_registro_costos.txt`](docs/evidencia_registro_costos.txt) | [b6883c5](https://github.com/EnzoGatica/asistente-pymes-ia/commit/b6883c5) |
| 14 | Pruebas unitarias del cliente | [`tests/test_cliente.py`](tests/test_cliente.py) | [2e8d282](https://github.com/EnzoGatica/asistente-pymes-ia/commit/2e8d282) |
| 15 | Pipeline de procesamiento de texto | [`src/pipeline_texto.py`](src/pipeline_texto.py), [`docs/evidencia_pipeline_antes_despues.txt`](docs/evidencia_pipeline_antes_despues.txt) | [b3b3f20](https://github.com/EnzoGatica/asistente-pymes-ia/commit/b3b3f20) |
| 16 | Métricas sobre las salidas del cliente | [`src/pipeline_texto.py`](src/pipeline_texto.py), [`resultados_metricas.json`](resultados_metricas.json) | [c1c5463](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c1c5463) |
| 17 | Interpretación y límites del pipeline | [`docs/limites_metrica.md`](docs/limites_metrica.md) | [8c1ebd4](https://github.com/EnzoGatica/asistente-pymes-ia/commit/8c1ebd4) |
| 18 | Chain de tres pasos | [`src/cadena_tres_pasos.py`](src/cadena_tres_pasos.py) | [193cad8](https://github.com/EnzoGatica/asistente-pymes-ia/commit/193cad8) |
| 19-20 | Enrutamiento condicional y chain de extremo a extremo | [`src/enrutamiento.py`](src/enrutamiento.py), [`docs/evidencia_enrutamiento.txt`](docs/evidencia_enrutamiento.txt) | [71543f0](https://github.com/EnzoGatica/asistente-pymes-ia/commit/71543f0) |
| 21-22 | Agente con herramientas y herramienta personalizada | [`src/agente.py`](src/agente.py) | [c8f317b](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c8f317b) |
| 23 | Límites de autonomía del agente | [`docs/limites_autonomia_agente.md`](docs/limites_autonomia_agente.md), [`trazas_agente.jsonl`](trazas_agente.jsonl) | [99e4d27](https://github.com/EnzoGatica/asistente-pymes-ia/commit/99e4d27) |
| 24-25 | Indexación del corpus y persistencia de embeddings | [`src/indexar_corpus.py`](src/indexar_corpus.py), [`corpus/`](corpus) | [32aa1e6](https://github.com/EnzoGatica/asistente-pymes-ia/commit/32aa1e6) |
| 26 | Recuperación y prompt dinámico con fuente citada | [`src/recuperacion.py`](src/recuperacion.py), [`docs/evidencia_recuperacion.txt`](docs/evidencia_recuperacion.txt) | [8bf31e9](https://github.com/EnzoGatica/asistente-pymes-ia/commit/8bf31e9) |
| 27 | Evaluación de la recuperación | [`src/evaluacion_recuperacion.py`](src/evaluacion_recuperacion.py), [`resultados_evaluacion.txt`](resultados_evaluacion.txt) | [e5e1811](https://github.com/EnzoGatica/asistente-pymes-ia/commit/e5e1811) |
| 28 | Latencia y costo del flujo RAG | [`src/registro_rag.py`](src/registro_rag.py), [`registros_latencia_costo.jsonl`](registros_latencia_costo.jsonl) | [3d9363c](https://github.com/EnzoGatica/asistente-pymes-ia/commit/3d9363c) |
| 29 | Laboratorio de personalización | [`src/dataset_tuning.py`](src/dataset_tuning.py), [`datos/dataset_tuning.jsonl`](datos/dataset_tuning.jsonl) | [46cdf72](https://github.com/EnzoGatica/asistente-pymes-ia/commit/46cdf72) |
| 30 | Decisión de personalización fundamentada | [`decision_personalizacion.md`](decision_personalizacion.md) | [dd9c4b6](https://github.com/EnzoGatica/asistente-pymes-ia/commit/dd9c4b6) |
| 31 | Logging estructurado e inyección de prompt | [`src/logging_rag.py`](src/logging_rag.py), [`docs/evidencia_logging_rag.txt`](docs/evidencia_logging_rag.txt) | [a5f5716](https://github.com/EnzoGatica/asistente-pymes-ia/commit/a5f5716) |
| 32 | Matriz de riesgos y versionado de prompts | [`src/matriz_riesgos.py`](src/matriz_riesgos.py), [`prompts/registro_prompts.json`](prompts/registro_prompts.json), [`docs/evidencia_gobernanza.txt`](docs/evidencia_gobernanza.txt) | [95afb94](https://github.com/EnzoGatica/asistente-pymes-ia/commit/95afb94) |
| S1 | **Gate 2** - Integración y orquestación | [`servicio_rag.py`](servicio_rag.py), [`tests/test_gate2.py`](tests/test_gate2.py), [`rubrica_gate2.py`](rubrica_gate2.py) | [c2dd433](https://github.com/EnzoGatica/asistente-pymes-ia/commit/c2dd433) |

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

## Registro del ensayo de instalación limpia (Gate 2)

- Fecha: 2026-10-22
- Procedimiento: `git clone` en una carpeta nueva, entorno virtual nuevo, `pip install -r requirements.txt`, `.env` desde `.env.example`, `python verificar_entorno.py`, `python -m pytest`, `python servicio_rag.py`.
- `verificar_entorno.py` detectó correctamente la llave sin completar ("Pendiente: definir OPENAI_API_KEY") y, ya completa, "Entorno listo para la corrida final".
- Pruebas: 70 passed. Servicio: índice creado desde cero en la primera corrida (`indice_creado`), dos respuestas con fuente citada, supervisión pausada y rechazada al responder "n", "Proceso terminado sin errores.", exit 0.
- Hallazgo corregido antes de este ensayo: `cargar_indice` fallaba al crear el índice desde cero (`delete` con lista vacía en Chroma). Lo detectó `tests/test_gate2.py` y se corrigió; el ensayo confirma que un clon nuevo ya no falla.
- Seguridad: `grep ana.perez logs/servicio_rag.log` sin resultados; `git status` limpio; `git ls-files` solo muestra `.env.example` (ni `.env`, ni `vectorstore/`, ni logs).
