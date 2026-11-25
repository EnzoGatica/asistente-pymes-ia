# Matriz de Pruebas

Fecha: 2026-11-25
Huella de la matriz: 83ac87caafa6
Escenarios: 6 de 6 cumplidos

| ID | Tipo | Escenario | Peticion | Esperado | Cubre | Resultado | Hallazgo |
|---|---|---|---|---|---|---|---|
| MP-01 | valido | mayúsculas y espacios sobrantes | `POST /consultas {"pregunta": "   ¿DESPACHAN A DICHATO?  ...` | 200; contiene '3.500'; contiene 'despacho.md' | RF-01, RF-02, CA-02 | PASA |  |
| MP-02 | invalido | cuerpo sin el campo pregunta | `POST /consultas {}` | 422; contiene 'pregunta' | RF-01 | PASA |  |
| MP-03 | borde | 501 caracteres, uno sobre el límite | `POST /consultas {"pregunta": "aaaaaaaaaaaaaaaaaaaaaaaaaa...` | 422; contiene '500' | RF-01 | PASA |  |
| MP-04 | borde | pedido bien escrito que no existe | `GET /pedidos/P-9999` | 404; contiene 'no_encontrado' | RF-03, CA-05 | PASA |  |
| MP-05 | invalido | pregunta hecha solo de espacios | `POST /consultas {"pregunta": "     "}` | 422; contiene 'entrada_invalida' | RF-01, CA-06 | PASA |  |
| MP-06 | borde | pregunta que corpus/ no cubre | `POST /consultas {"pregunta": "¿Cuál es la clave del wifi...` | 200; contiene 'No tengo información suficiente'; fuentes [] | RF-02, CA-03 | PASA |  |
