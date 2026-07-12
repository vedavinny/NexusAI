# Build context is the project root (see docker-compose.yml), so that the
# `backend` package path used in imports (e.g. `from backend.config...`)
# is preserved inside the image.
FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2 / sentence-transformers (torch) build steps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
