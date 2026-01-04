from .openai_client import OpenAIClient
from decouple import config

def generate_post(news_text: str) -> str:
    """
    Generates post via OpenAI.
    """
    api_key = config('OPENAI_API_KEY')
    client = OpenAIClient(api_key)
    result = client.generate_post(news_text)
    return result or "Ошибка генерации"