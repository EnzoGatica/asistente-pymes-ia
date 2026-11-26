# Verificación cruzada del despliegue

Revisor: Claude, asistente de IA (revisión diferida a pedido de Enzo Gatica)
Repositorio revisado: asistente-pymes-ia (rama main)
Fecha: 2026-11-26
Se siguió únicamente: README.md

## Resultado por criterio

- VC-1 (clon limpio): PASA - git clone de https://github.com/EnzoGatica/asistente-pymes-ia en una carpeta temporal nueva, commit b066544; git status limpio al terminar (.env y .venv quedan ignorados).
- VC-2 (configuración documentada): PASA - se copió .env.example a .env y se completó OPENAI_API_KEY (ENTORNO quedó en desarrollo); la sección Configuración explica las dos variables y /salud respondió "modelo": "configurado".
- VC-3 (arranque con un comando): PASA - docker compose up -d --build terminó en 1 min 38 s con api healthy e interfaz arrancando; del clon a la API respondiendo pasaron menos de 2 minutos. Ojo: el equipo ya tenía las capas de la imagen en caché y el volumen asistente-espiga_indice de ejecuciones anteriores, así que no se midió una construcción en frío del índice ni de la imagen.
- VC-4 (servicios sanos y alcanzables): PASA - docker compose ps mostró api e interfaz en healthy; http://127.0.0.1:8000/salud devolvió "estado": "ok" y http://127.0.0.1:8080 cargó la interfaz.
- VC-5 (comportamiento verificable): PASA - en la interfaz, "¿Despachan a Dichato?" respondió con $3.500 y fuentes ["despacho.md", "reclamos_devoluciones.md"]; GET /pedidos/P-1002 dio 200 con "estado": "entregado" y P-9999 dio 404 con "codigo": "no_encontrado"; python verificar_stack.py terminó en "7 de 7 comprobaciones cumplidas" (14 de 14 casos), pero solo después de crear el entorno virtual (hallazgo 1).
- VC-6 (sin secretos y apagado limpio): PASA - python buscar_secretos.py asistente-espiga/api:0.3 dio 5 de 5 (la imagen no guarda la llave); verificar_stack.py y luego docker compose down no dejaron contenedores del proyecto.

## Hallazgos

- Hallazgo 1 (VC-5): con el Python del sistema, python verificar_stack.py falla con "ModuleNotFoundError: No module named 'httpx2'". La sección Instalación decía que el entorno virtual "solo hace falta para ejecutar las pruebas o arrancar el servicio sin Docker", y el paso 5 de "Cómo comprobar que funciona" no lo pedía.
  Decisión: aceptado - el README ahora dice que la instalación también hace falta para los verificadores y el paso 5 pide el entorno virtual activo.
- Hallazgo 2 (VC-5): el paso 2 de "Cómo comprobar que funciona" decía que la respuesta "cita corpus/despacho.md", pero la interfaz muestra "despacho.md" en "fuentes", sin la carpeta. Quien compare al pie de la letra puede creer que falló.
  Decisión: aceptado - el paso 2 ahora dice que en "fuentes" aparece "despacho.md" (el archivo corpus/despacho.md).
