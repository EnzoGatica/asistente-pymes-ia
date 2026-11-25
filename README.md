# Asistente de consultas para pymes

Asistente de IA generativa para atender los mensajes que los clientes de una pyme (en el ejemplo, la Panadería La Espiga de Tomé, ficticia) mandan por WhatsApp o Instagram. Responde con la información oficial del negocio y cita el documento que respalda cada respuesta. Los datos son simulados.

Desde el Módulo 3 funciona como servicio web. Todas las operaciones quedan documentadas en http://127.0.0.1:8000/docs cuando el servicio está arriba:

- `GET /salud`: dice si el servicio está listo, en qué entorno corre y si tiene la clave del modelo.
- `POST /consultas`: recibe un JSON con el campo "pregunta" y devuelve "respuesta", "fuentes" y "trace_id".
- `GET /pedidos/{codigo}`: estado de un pedido simulado, con el formato P-0000 (por ejemplo P-1002).

Modelo: OpenAI `gpt-4.1-mini` desde el 25-11-2026, porque `gpt-4.1-nano` fue dado de baja (ver [decisión de modelo](docs/decision-arquitectura.md)); embeddings `text-embedding-3-small`; vector store Chroma; orquestación con LangChain y LangGraph; API con FastAPI; contenedores con Docker Compose. Diseño funcional completo en `docs/ficha_diseno_funcional.md`.

Proyecto de la Especialización en Desarrollo con IA Generativa (Accenture · Skillnest), construido bloque a bloque sobre la plantilla base del programa.

## Requisitos

- Docker con Compose. Comprueba con `docker compose version`.
- Los puertos 8000 y 8080 libres en tu equipo.
- Una llave de API de OpenAI ([crear una aquí](https://platform.openai.com/api-keys)).
- Para desarrollar o probar sin Docker: Python 3.14 (la misma versión que usa la imagen) y Git.

## Instalación

Solo hace falta para ejecutar las pruebas o arrancar el servicio sin Docker. Desde la raíz del repositorio:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

En Windows, la activación es `.venv\Scripts\activate` (en PowerShell, `.\.venv\Scripts\Activate.ps1`). El archivo `requirements.txt` trae solo lo que usa el servicio, y `requirements-dev.txt` le suma pytest.

## Configuración

1. Copia el archivo de ejemplo (en PowerShell: `Copy-Item .env.example .env`):

```
cp .env.example .env
```

2. Completa los valores en `.env`. El archivo `.env` está en `.gitignore` y nunca se sube.

- `OPENAI_API_KEY` (secreto): llave de la API de OpenAI. Si queda vacía, el servicio arranca igual, `/salud` informa "sin clave" y las consultas responden 503.
- `ENTORNO` (configuración): `desarrollo` o `produccion`. Por omisión, `desarrollo`.

La interfaz recibe la dirección de la API en la variable API_URL, que fija `compose.yaml` (http://api:8000 dentro de la red de Compose); no va en `.env`. Para comprobar la configuración sin mostrar la llave: `python verificar_entorno.py`.

## Cómo arrancar

Con Docker, la API y la interfaz web juntas:

```
docker compose up -d --build
```

Cuando termine, la solución queda en estas direcciones:

- API y su documentación: http://127.0.0.1:8000/docs
- Interfaz web: http://127.0.0.1:8080

Sin Docker, solo la API (con el entorno virtual activo):

```
uvicorn servicio.main:app --port 8000
```

### Uso por consola (Gates 1 y 2)

- Gate 1: `python main.py "Hola, ¿tienen marraquetas calientes?"` clasifica el mensaje y propone una respuesta.
- Gate 2: `python servicio_rag.py "¿Despachan a Penco?"` responde con fuentes. Sin argumentos corre dos consultas de ejemplo y el punto de supervisión humana, que pregunta "¿Aprobar? (s/n)".

La primera consulta crea el índice en `vectorstore/` a partir de `corpus/` (unos segundos); las siguientes lo reutilizan. En Docker el índice vive en el volumen "indice".

## Cómo comprobar que funciona

1. `docker compose ps` debe mostrar `api` e `interfaz` en `healthy`.
2. Abre http://127.0.0.1:8080, escribe "¿Despachan a Dichato?" y pulsa Preguntar: la respuesta menciona $3.500 y cita `corpus/despacho.md`.
3. `curl http://127.0.0.1:8000/salud` debe devolver "estado": "ok" y "modelo": "configurado".
4. `curl http://127.0.0.1:8000/pedidos/P-1002` devuelve el pedido con "estado": "entregado"; con P-9999 responde 404.
5. Opcional: `python verificar_stack.py` levanta todo, ejecuta siete comprobaciones, apaga y termina con "7 de 7 comprobaciones cumplidas".

## Cómo detener

```
docker compose down
```

Para borrar también el índice guardado en el volumen: `docker compose down -v`.

## Pruebas

```
python -m pytest -q
```

Las pruebas no llaman a la API de OpenAI: usan embeddings deterministas y un modelo simulado sobre el código real. `tests/test_api.py` recorre la tabla de casos de `casos.py` y `tests/parciales/` prueba cada componente por separado.

Verificadores de cada entrega (los que llaman al modelo real necesitan `.env` con la llave):

| Comando | Qué comprueba |
|---|---|
| `python verificar_ficha_completa.py` | Ficha de diseño funcional (Bloques 33 y 34) |
| `python verificar_servicio.py` | La documentación de la API y los criterios CA-01 a CA-06 contra el modelo real (Bloque 35) |
| `python cliente_externo.py` | La tabla de casos contra el servicio en marcha (Bloque 36) |
| `python registrar_pruebas.py` | Escribe `docs/registro_pruebas.md` (Bloque 36) |
| `python verificar_dockerfile.py` | Siete reglas del Dockerfile; con `interfaz/Dockerfile` revisa el de la interfaz (Bloque 37) |
| `python verificar_imagen.py asistente-espiga:0.3` | La imagen corre sin root, sana y pasa los 14 casos (Bloque 37) |
| `python buscar_secretos.py asistente-espiga/api:0.3` | Ningún secreto en archivos, git ni la imagen (Bloque 38) |
| `python verificar_stack.py` | El stack de Compose completo (Bloque 38) |
| `python verificar_entrega.py` | Composición, README, variables, puertos, verificación cruzada y secretos (Bloque 38) |
| `python verificar_parciales.py` | Plan y pruebas parciales de `docs/pruebas_parciales.md` (Bloque 39) |

### Scripts por bloque (Módulos 1 y 2)

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

## Decisiones técnicas

- **Modelo `gpt-4.1-mini` de OpenAI.** Se eligió `gpt-4.1-nano` por costo (Bloque 9) y se pasó al respaldo previsto cuando OpenAI lo dio de baja. Detalle en `docs/decision-arquitectura.md`.
- **RAG sobre `corpus/` con Chroma.** La información del negocio cambia (precios, horarios) y vive en documentos que la dueña puede editar; el índice se actualiza solo con los fragmentos que cambiaron. La comparación con fine-tuning está en `decision_personalizacion.md`.
- **Si el contexto no alcanza, no se citan fuentes.** Cuando el modelo declara que no tiene la información, el servicio responde un mensaje estándar con "fuentes" vacía en vez de pegar documentos que no respaldan nada.
- **Un contrato en cada borde.** La entrada se valida con pydantic (3 a 500 caracteres) y todos los errores tienen la forma "codigo" y "mensaje", sin detalles internos.
- **Secretos solo al ejecutar.** La llave entra por variables de entorno; nunca está en la imagen, en `compose.yaml` ni en git (`buscar_secretos.py` lo comprueba).
- **Dos contenedores.** La interfaz solo llama a la API: no tiene acceso al modelo ni a la llave.

## Limitaciones

- Los datos del negocio y los pedidos son simulados; no hay conexión con WhatsApp ni con un sistema de pedidos real.
- El corpus tiene 8 documentos: una pregunta que no está ahí no se puede responder, y el servicio lo dice.
- La detección de "sin información" busca frases como "no tengo información"; una respuesta evasiva escrita con otras palabras podría pasar con fuentes.
- El filtro de inyección es una lista de patrones: un ataque redactado de otra forma puede evadirlo (la segunda barrera es el prompt, que trata el contexto como datos).
- Cada consulta depende de la API de OpenAI: si no responde, el servicio devuelve 503.

## Estructura del repositorio

- `servicio/`: la API FastAPI (rutas, esquemas, errores, configuración y el puente con `servicio_rag.py`).
- `interfaz/`: la página web mínima y su contenedor.
- `src/`: componentes de los Módulos 1 y 2 (cliente, RAG, logging, gobernanza).
- `corpus/`: los 8 documentos del negocio.
- `prompts/`: banco de prompts y registro de versiones.
- `tests/`: pruebas de la API y de los Gates; `tests/parciales/` prueba cada componente.
- `docs/`: ficha de diseño, diagramas, decisiones, registros y evidencias de cada bloque.
- `compose.yaml` y `Dockerfile`: cómo se construye y se levanta.
- Los archivos `verificar_*.py`: comprobaciones ejecutables de cada entrega.

## Problemas frecuentes

- **Bind for 0.0.0.0:8000 failed: port is already allocated.** Otro programa usa el puerto (por ejemplo un uvicorn local). Detenlo o cambia el número de la izquierda en "ports" de `compose.yaml`.
- **`/salud` dice "sin clave" o las consultas responden 503.** Falta `OPENAI_API_KEY` en `.env`. Complétala y recrea los contenedores con `docker compose up -d`.
- **La interfaz responde 502.** La API no está disponible: revisa `docker compose logs api`.
- **La primera consulta tarda varios segundos.** Está creando el índice; las siguientes son más rápidas.
- **En PowerShell no se puede activar el entorno virtual.** Ejecuta `Set-ExecutionPolicy -Scope Process Bypass` o usa el Símbolo del sistema.

## Verificación cruzada

La revisión de un par que siga solo este README se registrará en docs/verificacion_cruzada.md (pendiente).

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

