# =============================================================================
# ROGER — Dockerfile unificado (backend + frontend)
#
# REQUISITOS ANTES DEL PRIMER BUILD:
#
#   1. Crear el .env en la raíz copiando .env.example y completar:
#        SECRET_KEY        — string largo y aleatorio
#        GROQ_API_KEY      — clave del proveedor LLM
#        SMTP_USER/PASSWORD — correo UCN para envío de emails
#        FRONTEND_URL      — http://IP-del-servidor
#
#   2. Actualizar el package-lock.json de leila (solo una vez, tras cambiar adapter):
#        cd leila && npm install
#      Commitear el package-lock.json antes de hacer el build.
#
# BUILD Y ARRANQUE:
#   docker compose up -d --build
#
# CREAR USUARIO ADMINISTRADOR (una sola vez, con los contenedores corriendo):
#   docker compose exec -it valeria python scripts/create_admin.py
#
# =============================================================================


# ─────────────────────────────────────────────────────────────
# LEILA — Frontend SvelteKit (Node / adapter-node)
# ─────────────────────────────────────────────────────────────

FROM node:20-alpine AS leila-builder
WORKDIR /app
COPY leila/package*.json ./
RUN npm ci
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

FROM node:20-alpine AS leila
WORKDIR /app
COPY --from=leila-builder /app/build ./build
COPY --from=leila-builder /app/package*.json ./
RUN npm ci --omit=dev
EXPOSE 3000
ENV PORT=3000 HOST=0.0.0.0
CMD ["node", "build/index.js"]


# ─────────────────────────────────────────────────────────────
# VALERIA — Backend FastAPI (Python 3.13)
# ─────────────────────────────────────────────────────────────

FROM python:3.13-slim AS valeria
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY valeria/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY valeria/ .

RUN mkdir -p /app/data /app/storage/images /app/uploads /app/logs \
    && chmod +x entrypoint.sh

EXPOSE 8000

# Aplica migraciones automáticamente y luego inicia el servidor
ENTRYPOINT ["./entrypoint.sh"]
