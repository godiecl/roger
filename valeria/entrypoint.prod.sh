#!/bin/sh
# =============================================================================
# Entrypoint de PRODUCCIÓN — Valeria.
#
# Diferencias vs entrypoint.sh (dev):
#   - UVICORN_WORKERS configurable (default 4).
#   - Sin --reload (autoreload no debe correr en prod).
#   - --proxy-headers / --forwarded-allow-ips para que detecte HTTPS detrás de nginx.
#   - Loglevel info, sin colores en logs (mejor para journald/loki).
#
# Convive con entrypoint.sh del repo. Usado por Dockerfile.prod.
# =============================================================================
set -e

echo "[valeria.prod] Aplicando migraciones de base de datos..."
alembic upgrade head

: "${UVICORN_WORKERS:=4}"
: "${UVICORN_PORT:=8000}"
: "${UVICORN_HOST:=0.0.0.0}"

echo "[valeria.prod] Iniciando uvicorn con ${UVICORN_WORKERS} workers en ${UVICORN_HOST}:${UVICORN_PORT}..."
exec uvicorn app.main:app \
    --host "${UVICORN_HOST}" \
    --port "${UVICORN_PORT}" \
    --workers "${UVICORN_WORKERS}" \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --log-level info \
    --no-use-colors
