from celery import Celery
from decouple import config
from app.news_parser.sites import HabrParser
from app.news_parser.telegram import TelegramParser
from app.models import NewsItem, SessionLocal, Keyword, Post, Source
from app.telegram.bot import publish_post_to_telegram
from app.ai.generator import generate_post
import os
import asyncio
import uuid

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

@celery.task
def collect_news_task():
    """
    Task: collect news from websites and save it in the database.
    """
    parser = HabrParser()
    news_items = parser.parse()

    db = SessionLocal()
    try:
        for item in news_items:
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

    return f"Collected {len(news_items)} news"

@celery.task
def collect_telegram_news_task():
    """
    Task: collect news from Telegram channels and save in the database.
    """
    db = SessionLocal()
    try:
        telegram_sources = db.query(Source).filter(Source.source_type == 'tg', Source.enabled == True).all()

        api_id = config('TELEGRAM_API_ID')
        api_hash = config('TELEGRAM_API_HASH')
        phone = config('TELEGRAM_PHONE')

        parser = TelegramParser(
            api_id=api_id,
            api_hash=api_hash,
            phone=phone
        )

        all_news = []
        for source in telegram_sources:
            news = asyncio.run(parser.parse(source.url, limit=10))
            all_news.extend(news)

        for item in all_news:
            if item.get('url') is None:
                continue

            existing = db.query(NewsItem).filter(NewsItem.url == item['url']).first()
            if not existing:
                news_item = NewsItem(
                    id=item.get('id', str(uuid.uuid4())),
                    title=item.get('title') or '',
                    url=item['url'],
                    summary=item.get('summary', ''),
                    source=item.get('source', 'telegram'),
                    published_at=item.get('published_at'),
                    raw_text=item.get('raw_text', '')
                )
                db.add(news_item)
        db.commit()

        return f"Collected {len(all_news)} news from Telegram"
    finally:
        db.close()

@celery.task
def filter_news_task():
    """
    Task: filter news by keywords.
    """
    db = SessionLocal()
    try:
        keywords = db.query(Keyword.word).all()
        keywords = [k[0] for k in keywords]

        news_items = db.query(NewsItem).all()

        filtered_news = []
        for item in news_items:
            if any(keyword.lower() in item.title.lower() or keyword.lower() in item.summary.lower() for keyword in keywords):
                filtered_news.append(item.id)

        return f"Filtered {len(filtered_news)} news"
    finally:
        db.close()

@celery.task
def generate_post_task(news_id: str):
    """
    Task: generate a post via AI.
    """
    db = SessionLocal()
    try:
        news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not news_item:
            return "News not found"

        generated_text = generate_post(news_item.summary)

        post = Post(
            news_id=news_item.id,
            generated_text=generated_text,
            status='generated'
        )
        db.add(post)
        db.commit()

        return f"Post for news {news_id} generated"
    finally:
        db.close()

@celery.task
def publish_post_task(post_id: str):
    """
    Task: publish a post in the Telegram channel.
    """
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post or post.status != 'generated':
            return "Post is not ready for publication"

        result = publish_post_to_telegram(post.generated_text)

        if result == 'published':
            post.status = 'published'
            db.commit()
            return f"Post {post_id} published"
        else:
            post.status = 'failed'
            db.commit()
            return f"Post {post_id} not published"
    finally:
        db.close()