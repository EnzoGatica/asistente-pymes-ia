# Diario de fricción

Fricciones reales que aparecieron al levantar y probar el proyecto entre el 22-10 y el 25-11-2026 siguiendo el README de cada momento. Cada una dice qué faltaba o confundía y en qué sección del README se resolvió.

- [Requisitos] El README del Gate 2 no decía que el Módulo 3 necesita Docker con Compose ni los puertos 8000 y 8080 libres.
- [Requisitos] No quedaba claro qué versión de Python usa la imagen; ahora el README dice Python 3.14, la misma del Dockerfile.
- [Instalación] Con solo requirements.txt no se podían correr las pruebas desde un clon limpio en la imagen; se separó requirements-dev.txt con pytest.
- [Instalación] El entorno local se llamaba venv y la guía decía .venv; se unificó en .venv en el README y ambos quedan en .gitignore.
- [Configuración] .env.example traía "tu_llave_aqui" como valor y la verificación de secretos pedía que el secreto viniera vacío.
- [Configuración] No se explicaba que sin clave el servicio arranca igual y /salud dice "sin clave".
- [Cómo arrancar] No había forma documentada de arrancar sin Docker para depurar; se agregó el comando con uvicorn.
- [Cómo comprobar] Las consultas respondían 503 y no había un paso para distinguir "sin clave" de "modelo dado de baja"; se agregó revisar /salud.
- [Pruebas] Los verificadores fallaban en Windows al leer la salida de docker compose (UnicodeDecodeError en cp1252).
- [Decisiones] El modelo gpt-4.1-nano fue dado de baja y no estaba escrito cuál era el respaldo previsto en el README.
- [Limitaciones] El servicio citaba fuentes cuando el modelo decía no tener la información, y eso no figuraba como límite conocido.
- [Estructura] Con servicio/, interfaz/, src/ y los verificadores en la raíz, no se entendía dónde estaba cada parte.
- [Problemas frecuentes] Un uvicorn local olvidado en el puerto 8000 hacía fallar docker compose up con "port is already allocated".
