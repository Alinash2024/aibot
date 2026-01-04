from app.tasks import celery

celery.conf.beat_schedule = {
    'collect-news-every-30-minutes': {
        'task': 'app.tasks.collect_news_task',
        'schedule': 1800,
    },
}

celery.conf.timezone = 'UTC'