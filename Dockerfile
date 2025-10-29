FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

RUN useradd -m appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=3s CMD curl -fsS http://127.0.0.1:${PORT:-10000}/health || exit 1

EXPOSE 10000
ENV PORT=10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



