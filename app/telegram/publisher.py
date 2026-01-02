from telethon import TelegramClient
from decouple import config
import asyncio

class TelegramPublisher:
    def __init__(self, api_id: str, api_hash: str, phone: str):
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.phone = phone

    async def start(self):
        await self.client.start(phone=self.phone)

    async def send_message(self, channel_username: str, message: str):
        await self.client.send_message(channel_username, message)
        return 'published'

    async def disconnect(self):
        await self.client.disconnect()

    def sync_send_message(self, channel_username: str, message: str):
        async def run():
            await self.start()
            result = await self.send_message(channel_username, message)
            await self.disconnect()
            return result

        return asyncio.run(run())