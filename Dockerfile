# Small, fast Python base
FROM python:3.11-slim

# Install ffmpeg and minimal deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# App files
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py filters.py ./

# Render (and many PaaS) set $PORT at runtime
ENV PORT=10000
EXPOSE 10000

CMD uvicorn app:app --host 0.0.0.0 --port $PORT
