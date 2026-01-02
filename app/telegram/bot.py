from .publisher import TelegramPublisher
from decouple import config

def publish_post_to_telegram(post_text: str):
    """
    Публикует пост в Telegram-канал.
    """
    api_id = config('TELEGRAM_API_ID')
    api_hash = config('TELEGRAM_API_HASH')
    phone = config('TELEGRAM_PHONE')
    channel_username = config('TELEGRAM_CHANNEL')

    publisher = TelegramPublisher(api_id, api_hash, phone)
    result = publisher.sync_send_message(channel_username, post_text)
    return result