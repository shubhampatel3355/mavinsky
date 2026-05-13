# ---------- Stage 1: Build ----------
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.13-slim

WORKDIR /app

# Install only the runtime PostgreSQL client library
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Expose the default Uvicorn port
EXPOSE 8000

# Run reconciliation and migrations on startup, then launch the server
CMD ["sh", "-c", "python reconcile_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
