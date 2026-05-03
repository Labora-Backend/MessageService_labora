# Build from repository root, e.g.: docker build -f MessageService/Dockerfile .
# WebSocket middleware reads JWT_PUBLIC_KEY_PATH (mounted volume).

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JWT_PUBLIC_KEY_PATH=/app/jwt_keys/public.pem

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && useradd -m -u 10001 appuser \
    && mkdir -p /app/jwt_keys \
    && rm -rf /var/lib/apt/lists/*

COPY MessageService/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=appuser:appuser MessageService/ /app/

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p 8000 project.asgi:application"]
