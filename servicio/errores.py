"""Formato común de errores: {"codigo": ..., "mensaje": ...} en 404, 405, 422, 500 y 503."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from servicio.logica import PedidoNoEncontrado, ServicioNoDisponible, servicio_rag

CODIGOS = {404: "no_encontrado", 405: "metodo_no_permitido", 422: "entrada_invalida"}


def error(estado, codigo, mensaje, headers=None):
    return JSONResponse(status_code=estado, content={"codigo": codigo, "mensaje": mensaje}, headers=headers)


def describir_validacion(errores):
    partes = []
    for e in errores:
        campo = ".".join(str(p) for p in e["loc"][1:]) or "cuerpo"
        partes.append(f"{campo}: {e['msg']}")
    return "; ".join(partes)


async def error_http(request, exc):
    return error(exc.status_code, CODIGOS.get(exc.status_code, "error_http"), str(exc.detail), getattr(exc, "headers", None))


async def error_validacion(request, exc):
    return error(422, "entrada_invalida", describir_validacion(exc.errors()))


async def pedido_no_encontrado(request, exc):
    return error(404, "no_encontrado", f"El pedido {exc.args[0]} no existe.")


async def servicio_no_disponible(request, exc):
    return error(503, "servicio_no_disponible", servicio_rag.ERROR_SERVICIO)


async def error_interno(request, exc):
    servicio_rag.evento("error_interno", 40, tipo=type(exc).__name__)
    return error(500, "error_interno", "Ocurrió un error inesperado. Intenta de nuevo en unos minutos.")


def registrar(app: FastAPI):
    app.add_exception_handler(HTTPException, error_http)
    app.add_exception_handler(RequestValidationError, error_validacion)
    app.add_exception_handler(PedidoNoEncontrado, pedido_no_encontrado)
    app.add_exception_handler(ServicioNoDisponible, servicio_no_disponible)
    app.add_exception_handler(Exception, error_interno)
