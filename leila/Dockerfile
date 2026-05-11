# syntax=docker/dockerfile:1
# build with:
#   time eatmydata docker buildx build --progress=plain --tag roger/leila:prod --file Dockerfile .
# run with:
#   docker run --rm -it -p 30000 --name leila-prod roger/leila:prod
#
ARG NODE_VERSION=24
ARG NPM_VERSION=11.14.1
#
# ---- builder image -----------------------------------------------------------
FROM node:${NODE_VERSION}-alpine AS builder
ARG NPM_VERSION

# Set environment variable for build
ENV VITE_API_URL=/api/v1
ENV VITE_APP_NAME=Roger
ENV VITE_APP_DESCRIPTION="Roger: Robert Gerstmann's Repository"
ENV VITE_ENABLE_SEMANTIC_SEARCH=true
ENV VITE_ENABLE_AI_NARRATIVES=true

# Set the working directory in the container
WORKDIR /app

# Check https://github.com/nodejs/docker-node/tree/main#nodealpine to understand
# why libc6-compat might be needed.
RUN set -ex; \
    apk -U upgrade --verbose && \
    apk add --no-cache --verbose \
        ca-certificates \
        coreutils \
        curl \
        gcompat \
        libc6-compat \
        musl \
        tree \
        tzdata \
    && \
    cp /usr/share/zoneinfo/America/Santiago /etc/localtime && \
    echo 'alias ll="ls --color=auto -alF"' >> /root/.profile && \
    echo 'alias ls="ls --color=auto -aF"' >> /root/.profile && \
    rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Install the dependencies and build the app
COPY package.json package-lock.json ./
RUN set -ex; \
    npm install -g npm@${NPM_VERSION} && \
    npm ci

# Copy the rest of the source code and build the app
COPY . .

# Build the application
RUN npm run build


# ---- runner image ------------------------------------------------------------
FROM node:${NODE_VERSION}-alpine AS runner
ARG NPM_VERSION

# Set environment variable for runtime
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the builder stage to the runner stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json /app/package-lock.json ./

# Install only production dependencies
RUN set -ex; \
    npm install -g npm@${NPM_VERSION} && \
    npm ci --omit=dev && \
    npm cache clean --force

# Port the application will run on
EXPOSE 3000

# Start the application
CMD ["node", "build/index.js"]
