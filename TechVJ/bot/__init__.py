from typing import Union, AsyncGenerator
import asyncio
import logging
from pyrogram import Client, types

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
        batch_size: int = 200,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[types.Message, None]:
        """
        Async generator to iterate through messages sequentially with batching
        and optional cancellation support.

        Args:
            chat_id (int | str): Target chat ID or username.
            limit (int): Total number of messages to retrieve.
            offset (int, optional): Starting message index. Defaults to 0.
            batch_size (int, optional): Number of messages per batch. Defaults to 200.
            cancel_event (asyncio.Event, optional): Event to cancel iteration. Defaults to None.

        Yields:
            types.Message: Telegram message object.
        """
        current = offset

        while current < limit:
            if cancel_event and cancel_event.is_set():
                logging.info("Message iteration cancelled")
                break

            current_batch_size = min(batch_size, limit - current)
            if current_batch_size <= 0:
                break

            try:
                messages = await self.get_messages(
                    chat_id, list(range(current, current + current_batch_size))
                )
            except Exception as e:
                logging.error(f"Error fetching messages: {e}")
                break

            for message in messages:
                yield message
                current += 1
