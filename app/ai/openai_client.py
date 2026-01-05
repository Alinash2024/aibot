import logging

from openai import OpenAI, RateLimitError, OpenAIError

from app.config import settings

logger = logging.getLogger(__name__)

client: OpenAI | None = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


def make_request(instructions: str, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str | None:
    if not client:
        raise ValueError("OPENAI_API_KEY is not set")
    if not settings.OPENAI_MODEL:
        raise ValueError("OPENAI_MODEL is not set")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        return None
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

    return response.choices[0].message.content