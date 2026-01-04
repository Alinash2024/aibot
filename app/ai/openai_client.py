import openai
from typing import Optional

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def generate_post(self, news_text: str) -> Optional[str]:
        """
        Generates post via OpenAI.
        """
        prompt = f"""
        Make a short, interesting description of the news for the Telegram channel, add an emoji, call to action.
        News: {news_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error API: {e}")
            return None