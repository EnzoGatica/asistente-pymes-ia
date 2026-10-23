# Asistente de consultas para pymes

Miniaplicación de IA generativa que recibe el mensaje de un cliente de una pyme (por ejemplo, una panadería de Tomé), lo **clasifica** (pedido, precio, horario, reclamo u otro, con urgencia de 1 a 3) y **propone una respuesta** breve, indicando si requiere atención humana. Usa la API de OpenAI (`gpt-4.1-nano`) con prompts de sistema y salida JSON validada.

Proyecto de la Especialización en Desarrollo con IA Generativa (Accenture · Skillnest), construido bloque a bloque sobre la plantilla base del programa.

## Requisitos

- Python 3.10 o superior
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

El `.env` está en `.gitignore`: nunca se sube al repositorio.

## Ejecución

Con el entorno virtual activo, desde la raíz del proyecto:

```bash
python main.py "Hola, ¿tienen marraquetas calientes? ¿Cuánto sale el kilo?"
```

(en macOS/Linux usa `python3`). Si no pasas el mensaje como argumento, el programa lo pide por consola. Salida esperada (el texto varía porque lo genera el modelo):

```
Categoría: precio (urgencia 2/3)
Respuesta del modelo: ¡Hola! Tenemos marraquetas en el día, pero el precio del kilo requiere atención humana.
Requiere atención humana: sí
Costo total: USD 0.0000516
Proceso terminado sin errores.
```

Si algo falla (llave inválida, sin conexión, mensaje vacío), el programa muestra `No se pudo completar la operación: <motivo>` en vez de un traceback.

### Otros scripts

| Comando | Qué hace |
|---|---|
| `python src/consumir_openai.py` | Prueba mínima de conexión: una pregunta y su costo |
| `python src/comparar_modelos.py` | Compara latencia y costo de `gpt-4.1-nano` vs `gpt-4.1-mini` (5 peticiones c/u) |
| `python prompts/test_consistencia.py` | Corre cada prompt del banco 3 veces y guarda `prompts/registro_resultados.json` |

## Estructura

```
main.py                      Punto de entrada de la miniaplicación
src/consumir_openai.py       armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json, calcular_costo
src/comparar_modelos.py      Medición real de dos modelos candidatos
prompts/banco.py             Banco de 3 prompts (clasificar, extraer pedido, responder)
prompts/test_consistencia.py Validación de consistencia del banco
prompts/registro_resultados.json  Resultado de la última validación
docs/diagrama_arquitectura.png    Diagrama de arquitectura (fuente: .svg)
docs/decision-arquitectura.md     Registro de la decisión de modelo, con tabla comparativa
docs/evidencia_*.txt              Evidencias de petición autenticada y manejo de errores
tests/                       Pruebas unitarias (Módulo 2)
```

## Documentación

- [Diagrama de arquitectura](docs/diagrama_arquitectura.png)
- [Decisión de arquitectura: elección de modelo](docs/decision-arquitectura.md)
- [Registro de consistencia del banco de prompts](prompts/registro_resultados.json)

## Registro del ensayo de instalación limpia

- Fecha: 2026-10-22
- Procedimiento: `git clone` del remoto en una carpeta nueva, entorno virtual nuevo, `pip install -r requirements.txt`, `.env` creado desde `.env.example`, `python main.py` siguiendo solo este README.
- Resultado: ver detalle abajo.
