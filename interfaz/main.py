"""Interfaz web mínima: una página que reenvía la pregunta a la API. No conoce el modelo ni la clave."""
import json
import os
import urllib.error
import urllib.request

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

API_URL = os.environ.get("API_URL", "http://api:8000")
app = FastAPI(title="Interfaz del asistente de la Panadería La Espiga")

PAGINA = """<!doctype html>
<meta charset="utf-8">
<title>Panadería La Espiga</title>
<h1>Asistente de la Panadería La Espiga</h1>
<input id="q" size="40" placeholder="Escribe tu pregunta">
<button onclick="preguntar()">Preguntar</button>
<pre id="r"></pre>
<script>
async function preguntar() {
  const q = encodeURIComponent(document.getElementById("q").value);
  const r = await fetch("/preguntar?texto=" + q);
  document.getElementById("r").textContent =
    JSON.stringify(await r.json(), null, 2);
}
</script>"""


@app.get("/", response_class=HTMLResponse)
def inicio():
    return PAGINA


@app.get("/salud")
def salud():
    return {"estado": "ok", "api": API_URL}


@app.get("/preguntar")
def preguntar(texto: str):
    datos = json.dumps({"pregunta": texto}).encode()
    peticion = urllib.request.Request(
        API_URL + "/consultas",
        data=datos,
        headers={"Content-Type": "application/json"},
    )
    try:
        # 30 s: la primera consulta indexa corpus/ y llama a OpenAI
        with urllib.request.urlopen(peticion, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return JSONResponse(json.loads(e.read()), status_code=e.code)
    except OSError:
        return JSONResponse(
            {
                "codigo": "api_no_disponible",
                "mensaje": "No se pudo contactar a la API.",
            },
            status_code=502,
        )
