# syntax=docker/dockerfile:1
# build with:
#   time eatmydata docker buildx build --progress=plain --tag roger/valeria:prod --file Dockerfile .
# run with:
#   docker run --rm -it -p 8000:8000 --name valeria-prod roger/valeria:prod
# first time setup (with container running):
#   docker exec -it valeria-prod python scripts/create_admin.py
#
ARG PYTHON_VERSION=3.13
# ---- builder image -----------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /app

# Set environment variables to optimize Python behavior in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_ROOT_USER_ACTION=ignore

# The requirements library
COPY requirements.txt .

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && \
    pip install --upgrade pip uv && \
    uv pip install --system --prefix=/opt/valeria -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# ---- runner image ------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runner
ARG PYTHON_VERSION

WORKDIR /app

# Set environment variables to optimize Python behavior in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH="/opt/valeria/bin:${PATH}"
ENV PYTHONPATH="/opt/valeria/lib/python${PYTHON_VERSION}/site-packages"

# Install dependencies, including build tools for any packages that require
# compilation, and then clean up to reduce image size
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        libimage-exiftool-perl \
        libpq5 \
    && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/data /app/storage/images /app/uploads /app/logs

COPY --from=builder /opt/valeria /opt/valeria

COPY . .

# Copy the production environment variables file into the container
COPY --chmod=755 .env.release /app/.env

COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Start the application using the entrypoint script, which will handle any
# necessary setup before launching the FastAPI server
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
