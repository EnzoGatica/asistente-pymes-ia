from typing import Annotated

from fastapi import FastAPI
from fastapi import Path as Ruta

from servicio import config, logica
from servicio.errores import registrar
from servicio.esquemas import Consulta, Error, EstadoPedido, Respuesta

app = FastAPI(
    title="Asistente de la Panadería La Espiga",
    version="0.3.0",
    description="Responde consultas de clientes con la información oficial del negocio y sus fuentes.",
)
registrar(app)

ENTRADA_INVALIDA = {422: {"model": Error, "description": "La entrada no cumple el esquema."}}


@app.get("/salud", tags=["sistema"], summary="Comprobar el servicio")
def salud():
    modelo = "configurado" if config.modelo_configurado() else "sin clave"
    return {"estado": "ok", "entorno": config.entorno(), "modelo": modelo}


@app.post(
    "/consultas",
    response_model=Respuesta,
    tags=["consultas"],
    summary="Consultar la información del negocio",
    responses={**ENTRADA_INVALIDA, 503: {"model": Error, "description": "El proveedor del modelo no responde."}},
)
def consultar(consulta: Consulta):
    """Devuelve la respuesta, los documentos que la respaldan y el trace_id de la consulta."""
    texto, fuentes, trace_id = logica.responder(consulta.pregunta)
    return Respuesta(respuesta=texto, fuentes=fuentes, trace_id=trace_id)


@app.get(
    "/pedidos/{codigo}",
    response_model=EstadoPedido,
    tags=["pedidos"],
    summary="Consultar el estado de un pedido",
    responses={**ENTRADA_INVALIDA, 404: {"model": Error, "description": "El pedido no existe."}},
)
def consultar_pedido(codigo: Annotated[str, Ruta(pattern=r"^P-\d{4}$", description="Código como P-1001.")]):
    """Devuelve el estado del pedido según los datos simulados."""
    return logica.estado_pedido(codigo)
