from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from pyrogram.raw.types.messages import Messages
from TechVJ.server.exceptions import FIleNotFound


async def parse_file_id(message: Message) -> Optional[FileId]:
    """Decode and return the FileId of the media in a message."""
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)
    return None


async def parse_file_unique_id(message: Message) -> Optional[str]:
    """Return the unique file ID of the media in a message."""
    media = get_media_from_message(message)
    if media:
        return getattr(media, "file_unique_id", None)
    return None


async def get_file_ids(client: Client, chat_id: int, message_id: int) -> Optional[FileId]:
    """
    Retrieves the FileId object and metadata from a message in a chat.
    Raises FIleNotFound if the message is empty.
    """
    message = await client.get_messages(chat_id, message_id)
    if not message:
        raise FIleNotFound
    media = get_media_from_message(message)
    if not media:
        raise FIleNotFound
    file_unique_id = await parse_file_unique_id(message)
    file_id = await parse_file_id(message)
    if file_id:
        setattr(file_id, "file_size", getattr(media, "file_size", 0))
        setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
        setattr(file_id, "file_name", getattr(media, "file_name", ""))
        setattr(file_id, "unique_id", file_unique_id)
    return file_id


def get_media_from_message(message: Message) -> Optional[Any]:
    """Returns the first media object found in the message."""
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media
    return None


def get_hash(message: Message) -> str:
    """Returns a short hash derived from the file_unique_id."""
    media = get_media_from_message(message)
    return getattr(media, "file_unique_id", "")[:6] if media else ""


def get_name(message: Message) -> str:
    """Returns the file name of the media if it exists."""
    media = get_media_from_message(message)
    return getattr(media, "file_name", "") if media else ""


def get_media_file_size(message: Message) -> int:
    """Returns the size of the media file in bytes."""
    media = get_media_from_message(message)
    return getattr(media, "file_size", 0) if media else 0