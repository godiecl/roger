# syntax=docker/dockerfile:1
# build with:
#   time eatmydata docker buildx build --progress=plain --tag roger/valeria:prod --file Dockerfile .
# run with:
#   docker run --rm -it -p 80000 --name valeria-prod roger/valeria:prod
# first time setup (with container running):
#   docker exec -it valeria-prod python scripts/create_admin.py
#
ARG PYTHON_VERSION=3.13
# ---- runner image ------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runner

# Set environment variables to optimize Python behavior in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# The requirements library
COPY requirements.txt .

# Install dependencies, including build tools for any packages that require
# compilation, and then clean up to reduce image size
RUN set -ex; \
    apt-get update && \
    apt-get upgrade && \
    apt-get install -y --no-install-recommends \
        libimage-exiftool-perl \
        build-essential \
        libpq-dev \
    && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove \
        build-essential \
        libpq-dev \
    && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/data /app/storage/images /app/uploads /app/logs

COPY . .

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start the application using the entrypoint script, which will handle any
# necessary setup before launching the FastAPI server
ENTRYPOINT ["/entrypoint.sh"]
