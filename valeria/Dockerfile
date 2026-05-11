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

# The requirements library
COPY requirements.txt .

RUN set -ex; \
    apt-get update && \
    apt-get upgrade && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && \
    pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt --root-user-action && \
    rm -rf /var/lib/apt/lists/*

# ---- runner image ------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runner

WORKDIR /app

# Set environment variables to optimize Python behavior in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PATH="/install/bin:${PATH}"
ENV PYTHONPATH="/install/lib/python${PYTHON_VERSION}/site-packages"

# Install dependencies, including build tools for any packages that require
# compilation, and then clean up to reduce image size
RUN set -ex; \
    apt-get update && \
    apt-get upgrade && \
    apt-get install -y --no-install-recommends \
        libimage-exiftool-perl \
        libpq5 \
    && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/data /app/storage/images /app/uploads /app/logs

COPY --from=builder /install /install

COPY . .

COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Start the application using the entrypoint script, which will handle any
# necessary setup before launching the FastAPI server
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
