# Revisión del alcance

Revisor: Claude, asistente de IA (revisión diferida a pedido de Enzo Gatica)
Fecha: 2026-11-26

- Hallazgo 1 (criterio 4): CA-07 y CA-08 se comprueban con "las 10 consultas de prueba de tests/consultas_prueba.json", pero ese archivo no existe en el repositorio. Tal como están, nadie puede decidir si se cumplen: no se sabe qué 10 preguntas medir ni cuyo texto buscar en el log.
  Decisión: aceptado. Cambio: se crea tests/consultas_prueba.json con 10 preguntas (nueve sobre temas de corpus/ y una que no cubre) y la ficha lo nombra también en el hito que comprueba CA-07 y CA-08.
- Hallazgo 2 (criterio 5): H5 junta en 6 h tres trabajos distintos (pruebas de RNF-01 y RNF-02, documentación y ensayo de la defensa). Es el hito más largo y el único sin un entregable claro: si a mitad de camino quedan 2 h, no se sabe qué parte está hecha.
  Decisión: aceptado. Cambio: H5 queda en 3 h solo con las pruebas de CA-07 y CA-08, y un H6 de 3 h cubre el README de despliegue y el ensayo, comprobado con CA-09. El total sigue en 14 h contra un tope de 16 h.
- Hallazgo 3 (criterio 2): RF-04 (aprobación humana del prompt) está como Deseable y la sección 3 le asigna LangGraph, pero no tiene criterio de aceptación ni hito. Queda en el alcance sin forma de saber si se entregó.
  Decisión: aplazado. El MVP no depende de RF-04 y agregarle hito y criterio ahora no cabe en el margen; se decide al planificar el Capstone si se le escribe un CA o se pasa a Fuera de alcance.

Acierto: el problema (sección 1) está cuantificado sin nombrar la solución (150 mensajes a la semana, 3 minutos cada uno, 7,5 horas) y los criterios incluyen tres casos negativos decidibles: CA-03 (pregunta sin cobertura), CA-05 (pedido inexistente, 404) y CA-06 (pregunta vacía, 422 sin consumo del modelo).
