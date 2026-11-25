from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

TextoPregunta = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)
]


class Consulta(BaseModel):
    pregunta: TextoPregunta = Field(
        description="Pregunta del cliente, en lenguaje natural (3 a 500 caracteres).",
        examples=["¿Despachan a Dichato?"],
    )


class Respuesta(BaseModel):
    respuesta: str = Field(description="Texto de la respuesta para el cliente.")
    fuentes: list[str] = Field(
        description="Documentos de corpus/ que la respaldan; vacía si corpus/ no cubre la pregunta."
    )
    trace_id: str = Field(description="Identificador de la consulta en logs/servicio_rag.log.")


class EstadoPedido(BaseModel):
    codigo: str = Field(description="Código del pedido simulado, por ejemplo P-1001.")
    estado: str = Field(description="Estado según los datos simulados de src/negocio.py.")
    total: int = Field(description="Total del pedido en pesos chilenos.")
    historial: list[str] = Field(description="Eventos del pedido, del más antiguo al más reciente.")


class Error(BaseModel):
    codigo: str = Field(description="Código corto del error, por ejemplo no_encontrado.")
    mensaje: str = Field(description="Explicación del error, sin detalles internos.")
