import openai
import os
from typing import Optional

class OpenAIClient:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_post(self, news_text: str) -> Optional[str]:
        """
        Генерирует пост через OpenAI API.
        """
        prompt = f"""
        Сделай краткое, интересное описание новости для Telegram-канала, добавь emoji, call to action.
        Новость: {news_text}
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Ошибка API: {e}")
            return None