FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir uv && \
    pip install --no-cache-dir -e .

COPY . .

RUN mkdir -p sessions

CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info", "--pool=solo"]