# =============================================================================
# ROGER — Valeria (Backend FastAPI)
#
# REQUISITOS ANTES DE HACER BUILD:
#   1. Crear el archivo .env en la raíz del repositorio copiando .env.example
#      y completando al menos estas variables obligatorias:
#
#        SECRET_KEY=<string largo y aleatorio>
#        GROQ_API_KEY=<tu clave de Groq>       ← o la del proveedor LLM que uses
#        SMTP_USER=<correo UCN>
#        SMTP_PASSWORD=<contraseña>
#        FRONTEND_URL=<http://IP-del-servidor>
#
# BUILD Y ARRANQUE (desde la raíz del repositorio):
#   docker compose up -d --build
#
# PRIMER USO — crear usuario administrador (una sola vez, contenedor corriendo):
#   docker compose exec -it valeria python scripts/create_admin.py
#
# =============================================================================

FROM python:3.13-slim

WORKDIR /app

# ExifTool para procesar archivos RAW (CR3, NEF, ARW)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/storage/images /app/uploads /app/logs

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Aplica migraciones automáticamente antes de iniciar el servidor
ENTRYPOINT ["/entrypoint.sh"]
