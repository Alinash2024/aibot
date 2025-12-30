# AI Telegram Post Generator

Проект по ТЗ: автоматический парсинг новостей, генерация постов через GPT, публикация в Telegram.

## Технологии:
- Python 3.14.2
- FastAPI
- Celery
- Redis
- Telethon
- OpenAI API

## Установка:
1. `git clone ...`
2. `uv venv --python 3.14`
3. `uv sync`
4. `cp .env.example .env` и заполнить
5. `uvicorn app.main:app --reload`