from celery.schedules import crontab

celery.conf.beat_schedule = {
    'collect-news-every-30-minutes': {
        'task': 'app.tasks.collect_news_task',
        'schedule': 1800,  # 30 минут
    },
}

celery.conf.timezone = 'UTC'