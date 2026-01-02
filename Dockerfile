FROM python:3.14-slim

WORKDIR /app

# Установка системных зависимостей (если нужны)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем pyproject.toml
COPY pyproject.toml ./

# Установка uv и зависимостей через pip
RUN pip install --no-cache-dir uv && \
    pip install --no-cache-dir -e .

# Копируем весь код (после установки зависимостей — для кэша)
COPY . .

# Папка для сессий Telethon
RUN mkdir -p sessions

# Запуск по умолчанию (переопределяется в docker-compose)
CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info", "--pool=solo"]