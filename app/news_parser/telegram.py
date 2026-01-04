from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import Message
from datetime import datetime
import asyncio
import logging
from abc import ABC
import uuid

logger = logging.getLogger(__name__)


class TelegramParser(ABC):
    def __init__(self, api_id: str, api_hash: str, phone: str):
        self.client = TelegramClient('session_' + phone, api_id, api_hash)
        self.phone = phone
        self.source = 'telegram'

    async def connect(self):
        """Initialize the Telegram client connection"""
        await self.client.start(phone=self.phone)
        logger.info("Telegram client connected successfully")

    async def parse(self, channel_username: str, limit: int = 10):
        """
        Parse messages from a Telegram channel

        Args:
            channel_username: Username of the channel to parse
            limit: Number of messages to retrieve

        Returns:
            List of news items matching the NewsItem model structure
        """
        if not self.client.is_connected():
            await self.connect()

        news_items = []

        try:
            channel = await self.client.get_entity(channel_username)

            async for message in self.client.iter_messages(
                    channel,
                    limit=limit,
                    filter=None
            ):
                if isinstance(message, Message) and message.message:
                    try:
                        title = message.message[:100] if len(message.message) > 100 else message.message
                        summary = message.message
                        url = f"https://t.me/{channel_username}/{message.id}" if message.id else None
                        dt = message.date if message.date else datetime.utcnow()

                        news_item = {
                            'id': str(uuid.uuid4()),
                            'title': title,
                            'url': url,
                            'summary': summary,
                            'source': f"{self.source}:{channel_username}",
                            'published_at': dt,
                            'raw_text': message.message
                        }

                        news_items.append(news_item)

                    except Exception as e:
                        logger.error(f"Error processing message {message.id}: {e}")
                        continue

        except FloodWaitError as e:
            logger.error(f"Flood wait error: {e}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Error parsing Telegram channel {channel_username}: {e}")

        return news_items

    async def disconnect(self):
        """Disconnect the Telegram client"""
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info("Telegram client disconnected")
