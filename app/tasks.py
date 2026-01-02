from celery import Celery
from decouple import config
from app.news_parser.sites import HabrParser
from app.news_parser.telegram import TelegramParser
from app.models import NewsItem, SessionLocal, Keyword, Post, Source
import os
import openai
import asyncio
from telethon import TelegramClient
from sqlalchemy.orm import sessionmaker
import uuid

# Подключение к Redis
celery = Celery(
    'aibot',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Настройка OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@celery.task
def collect_news_task():
    """
    Задача: собрать новости с сайтов и сохранить в БД.
    """
    parser = HabrParser()
    news_items = parser.parse()

    db = SessionLocal()
    try:
        for item in news_items:
            # Проверяем, нет ли уже такой новости
            existing = db.query(NewsItem).filter(NewsItem.url == item['url']).first()
            if not existing:
                news_item = NewsItem(
                    id=item['id'],
                    title=item['title'],
                    url=item['url'],
                    summary=item['summary'],
                    source=item['source'],
                    published_at=item['published_at'],
                    raw_text=item['raw_text']
                )
                db.add(news_item)
        db.commit()
    finally:
        db.close()

    return f"Собрано {len(news_items)} новостей"

@celery.task
def collect_telegram_news_task():
    """
    Задача: собрать новости из Telegram-каналов и сохранить в БД.
    """
    db = SessionLocal()
    try:
        # Получить Telegram-источники
        telegram_sources = db.query(Source).filter(Source.source_type == 'tg', Source.enabled == True).all()

        # Загрузка переменных через decouple
        api_id = config('TELEGRAM_API_ID')
        api_hash = config('TELEGRAM_API_HASH')
        phone = config('TELEGRAM_PHONE')

        parser = TelegramParser(
            api_id=api_id,
            api_hash=api_hash,
            phone=phone  # <-- Передаём phone
        )

        all_news = []
        for source in telegram_sources:
            # Пример: source.url содержит @username
            news = asyncio.run(parser.parse(source.url, limit=10))
            all_news.extend(news)

        # Сохранить новости в базу
        for item in all_news:
            # Пропустить, если нет URL (нельзя сравнить)
            if item.get('url') is None:
                continue

            # Проверить, нет ли уже такой новости
            existing = db.query(NewsItem).filter(NewsItem.url == item['url']).first()
            if not existing:
                # Убедиться, что обязательные поля не None
                news_item = NewsItem(
                    id=item.get('id', str(uuid.uuid4())),
                    title=item.get('title') or '',  # Обязательное поле
                    url=item['url'],  # Уже проверили, что не None
                    summary=item.get('summary', ''),
                    source=item.get('source', 'telegram'),
                    published_at=item.get('published_at'),
                    raw_text=item.get('raw_text', '')
                )
                db.add(news_item)
        db.commit()

        return f"Собрано {len(all_news)} новостей из Telegram"
    finally:
        db.close()

@celery.task
def filter_news_task():
    """
    Задача: отфильтровать новости по ключевым словам.
    """
    db = SessionLocal()
    try:
        # Получаем ключевые слова
        keywords = db.query(Keyword.word).all()
        keywords = [k[0] for k in keywords]

        # Получаем все новости
        news_items = db.query(NewsItem).all()

        filtered_news = []
        for item in news_items:
            if any(keyword.lower() in item.title.lower() or keyword.lower() in item.summary.lower() for keyword in keywords):
                filtered_news.append(item.id)

        return f"Отфильтровано {len(filtered_news)} новостей"
    finally:
        db.close()

@celery.task
def generate_post_task(news_id: str):
    """
    Задача: сгенерировать пост через AI.
    """
    db = SessionLocal()
    try:
        news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not news_item:
            return "Новость не найдена"

        # Промпт для GPT
        prompt = f"""
        Сделай краткое, интересное описание новости для Telegram-канала, добавь emoji, call to action.
        Новость: {news_item.title}
        Описание: {news_item.summary}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        generated_text = response.choices[0].message['content'].strip()

        # Сохраняем сгенерированный пост
        post = Post(
            news_id=news_item.id,
            generated_text=generated_text,
            status='generated'
        )
        db.add(post)
        db.commit()

        return f"Пост для новости {news_id} сгенерирован"
    finally:
        db.close()

@celery.task
def publish_post_task(post_id: str):
    """
    Задача: опубликовать пост в Telegram-канал.
    """
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post or post.status != 'generated':
            return "Пост не готов к публикации"

        # Подключение к Telegram
        api_id = int(config('TELEGRAM_API_ID'))
        api_hash = config('TELEGRAM_API_HASH')
        channel_username = config('TELEGRAM_CHANNEL')

        client = TelegramClient('session_name', api_id, api_hash)
        client.start()

        # Отправка поста
        client.send_message(channel_username, post.generated_text)

        # Обновляем статус
        post.status = 'published'
        db.commit()

        return f"Пост {post_id} опубликован"
    finally:
        db.close()
        if 'client' in locals():
            client.disconnect()

# Настройка расписания для Celery Beat
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'collect-site-news': {
        'task': 'app.tasks.collect_news_task',
        'schedule': crontab(minute='*/30'),  # каждые 30 минут
    },
    'collect-telegram-news': {
        'task': 'app.tasks.collect_telegram_news_task',
        'schedule': crontab(minute='*/30'),  # каждые 30 минут
    },
}