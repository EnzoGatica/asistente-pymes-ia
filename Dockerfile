FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY servicio/ servicio/
COPY src/ src/
COPY prompts/ prompts/
COPY corpus/ corpus/
COPY servicio_rag.py .

# vectorstore/ y logs/ los escribe el servicio en tiempo de ejecución (en compose son volúmenes)
RUN useradd --create-home --uid 10001 app \
    && mkdir -p vectorstore logs \
    && chown app:app vectorstore logs
USER app

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request as u; \
u.urlopen('http://127.0.0.1:8000/salud')"

CMD ["uvicorn", "servicio.main:app", "--host", "0.0.0.0", "--port", "8000"]
