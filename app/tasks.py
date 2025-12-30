from celery import Celery
from app.news_parser.sites import HabrParser
from app.models import NewsItem, SessionLocal, Keyword, Post
import os
import openai
from telethon import TelegramClient

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

from telethon import TelegramClient

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
        api_id = int(os.getenv('TELEGRAM_API_ID'))
        api_hash = os.getenv('TELEGRAM_API_HASH')
        channel_username = os.getenv('TELEGRAM_CHANNEL')

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
        client.disconnect()
