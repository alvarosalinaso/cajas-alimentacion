FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app
COPY requirements-render.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt
COPY . .
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8055

# Pipeline: docker run <img> python -m cajas_alimentacion --no-sync
CMD ["sh", "-c", "gunicorn dashboard:server --bind 0.0.0.0:${PORT:-8055} --workers 2 --timeout 120"]
