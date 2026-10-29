# syntax=docker/dockerfile:1.4

ARG ERPNEXT_VERSION=v16.20.0

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --silent || npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: ERPNext + Brokerage Module
FROM frappe/erpnext:${ERPNEXT_VERSION} AS runner

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe/frappe-bench

RUN mkdir -p apps/brokerage_module

COPY --chown=frappe:frappe pyproject.toml README.md license.txt ./apps/brokerage_module/
COPY --chown=frappe:frappe brokerage_module/ ./apps/brokerage_module/brokerage_module/

COPY --chown=frappe:frappe --from=frontend-builder \
    /app/brokerage_module/public/frontend/ \
    ./apps/brokerage_module/brokerage_module/public/frontend/

RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e ./apps/brokerage_module

RUN printf "frappe\nerpnext\nbrokerage_module\n" > /home/frappe/frappe-bench/sites/apps.txt

RUN bench build --app brokerage_module

EXPOSE 8000

CMD ["bench", "serve", "--port", "8000"]

