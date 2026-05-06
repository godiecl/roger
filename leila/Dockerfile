# =============================================================================
# ROGER — Leila (Frontend SvelteKit)
#
# REQUISITO ANTES DE HACER BUILD:
#   El package-lock.json debe estar actualizado con adapter-node.
#   Si es la primera vez o se cambió el package.json, correr una vez localmente:
#
#     cd leila
#     npm install
#
#   Luego commitear el package-lock.json actualizado. Después de eso,
#   el build de Docker funciona sin instalar nada más en la máquina.
#
# BUILD Y ARRANQUE (desde la raíz del repositorio):
#   docker compose up -d --build
#
# NOTA SOBRE VITE_API_URL:
#   Las variables VITE_ se fijan en tiempo de build, no en runtime.
#   Por defecto se usa /api/v1 (relativa), que funciona con nginx
#   sirviendo frontend y backend bajo el mismo dominio y puerto.
#
# =============================================================================

# Etapa 1 — Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=/api/v1
ARG VITE_APP_NAME=ROGER
ARG VITE_APP_DESCRIPTION=Archivo Robert Gerstmann
ARG VITE_ENABLE_SEMANTIC_SEARCH=true
ARG VITE_ENABLE_AI_NARRATIVES=true

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_DESCRIPTION=$VITE_APP_DESCRIPTION
ENV VITE_ENABLE_SEMANTIC_SEARCH=$VITE_ENABLE_SEMANTIC_SEARCH
ENV VITE_ENABLE_AI_NARRATIVES=$VITE_ENABLE_AI_NARRATIVES

RUN npm run build

# Etapa 2 — Runtime (solo lo necesario para correr)
FROM node:20-alpine AS runtime

WORKDIR /app

COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./

RUN npm ci --omit=dev

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0

CMD ["node", "build/index.js"]
