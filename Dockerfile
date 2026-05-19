# =============================================================================
# ROGER — Dockerfile multi-stage (backend + frontend)
#
# REQUISITOS ANTES DEL PRIMER BUILD:
#
#   1. Crear el .env en la raíz copiando .env.example y completar:
#        SECRET_KEY        — string largo y aleatorio (openssl rand -hex 32)
#        GROQ_API_KEY      — clave del proveedor LLM
#        SMTP_USER/PASSWORD — correo UCN para envío de emails
#        FRONTEND_URL      — http://IP-del-servidor
#
#   2. Actualizar el package-lock.json de leila (solo una vez, tras cambiar adapter):
#        cd leila && npm install
#      Commitear el package-lock.json antes de hacer el build.
#
# BUILD Y ARRANQUE (primera vez):
#   docker compose build
#   docker compose run --rm valeria-migrate   # aplica migraciones una sola vez
#   docker compose up -d
#
# DEPLOYS POSTERIORES:
#   docker compose build
#   docker compose run --rm valeria-migrate
#   docker compose up -d
#
# CREAR USUARIO ADMINISTRADOR (una sola vez, con los contenedores corriendo):
#   docker compose exec valeria python scripts/create_admin.py
#
# =============================================================================


# ─────────────────────────────────────────────────────────────
# LEILA — stage 1: instalar dependencias (capa cacheable)
# ─────────────────────────────────────────────────────────────

FROM node:20-alpine AS leila-deps
WORKDIR /app
COPY leila/package*.json ./
RUN npm ci


# ─────────────────────────────────────────────────────────────
# LEILA — stage 2: compilar el build de producción
# ─────────────────────────────────────────────────────────────

FROM node:20-alpine AS leila-build
WORKDIR /app
COPY --from=leila-deps /app/node_modules ./node_modules
COPY leila/ .

ARG VITE_API_URL=/api/v1
ARG VITE_APP_NAME=ROGER
ARG VITE_APP_DESCRIPTION=Archivo Robert Gerstmann
ARG VITE_ENABLE_SEMANTIC_SEARCH=true
ARG VITE_ENABLE_AI_NARRATIVES=true

ENV VITE_API_URL=$VITE_API_URL \
    VITE_APP_NAME=$VITE_APP_NAME \
    VITE_APP_DESCRIPTION=$VITE_APP_DESCRIPTION \
    VITE_ENABLE_SEMANTIC_SEARCH=$VITE_ENABLE_SEMANTIC_SEARCH \
    VITE_ENABLE_AI_NARRATIVES=$VITE_ENABLE_AI_NARRATIVES

RUN npm run build


# ─────────────────────────────────────────────────────────────
# LEILA — stage 3: imagen de runtime (solo build + prod deps)
# ─────────────────────────────────────────────────────────────

FROM node:20-alpine AS leila
WORKDIR /app
COPY --from=leila-build /app/build ./build
COPY --from=leila-build /app/package*.json ./
RUN npm ci --omit=dev
EXPOSE 3000
ENV PORT=3000 HOST=0.0.0.0
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1
CMD ["node", "build/index.js"]


# ─────────────────────────────────────────────────────────────
# VALERIA — stage 1: base con dependencias de sistema runtime
# ─────────────────────────────────────────────────────────────

FROM python:3.13-slim AS valeria-base
RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*


# ─────────────────────────────────────────────────────────────
# VALERIA — stage 2: compilar wheels (con gcc; no va a runtime)
# ─────────────────────────────────────────────────────────────

FROM valeria-base AS valeria-build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY valeria/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# ─────────────────────────────────────────────────────────────
# VALERIA — stage 3: imagen de runtime (sin gcc, sin caché pip)
# ─────────────────────────────────────────────────────────────

FROM valeria-base AS valeria-runtime
WORKDIR /app

# Copiar paquetes compilados desde el stage de build
COPY --from=valeria-build /usr/local/lib/python3.13/site-packages \
                          /usr/local/lib/python3.13/site-packages
COPY --from=valeria-build /usr/local/bin /usr/local/bin

COPY valeria/ .

RUN mkdir -p /app/data /app/storage/images /app/uploads /app/logs

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ─────────────────────────────────────────────────────────────
# VALERIA-MIGRATE — one-shot: aplica migraciones Alembic
# Se usa como servicio separado en docker-compose, no como entrypoint.
# ─────────────────────────────────────────────────────────────

FROM valeria-runtime AS valeria-migrate
CMD ["alembic", "upgrade", "head"]
