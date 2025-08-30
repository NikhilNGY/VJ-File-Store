from pyrogram import Client, types
from config import API_ID, API_HASH, BOT_TOKEN
from typing import Union, Optional, AsyncGenerator

class StreamXBot(Client):
    def __init__(self):
        super().__init__(
            name="vjfiletolink",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

# ✅ Initialize global bot and dictionaries
StreamBot = StreamXBot()
multi_clients: dict[int, StreamXBot] = {0: StreamBot}
work_loads: dict[int, int] = {0: 0}
