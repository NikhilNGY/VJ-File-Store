from typing import Any, Optional, Union
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.file_id import FileId
from TechVJ.server.exceptions import FileNotFound


async def parse_file_id(message: Message) -> Optional[FileId]:
    """Decode and return the FileId from a message's media."""
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)
    return None


async def parse_file_unique_id(message: Message) -> Optional[str]:
    """Return the unique file ID from a message's media."""
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id
    return None


async def get_file_ids(client: Client, chat_id: int, message_id: int) -> FileId:
    """
    Fetch a message and return its media information as a FileId object
    with additional attributes like file_size, mime_type, file_name, and unique_id.
    """
    message = await client.get_messages(chat_id, message_id)
    if message.empty:
        raise FileNotFound(f"Message {message_id} not found in chat {chat_id}.")

    media = get_media_from_message(message)
    if not media:
        raise FileNotFound(f"No media found in message {message_id}.")

    file_id_obj = await parse_file_id(message)
    file_unique_id = await parse_file_unique_id(message)

    setattr(file_id_obj, "file_size", getattr(media, "file_size", 0))
    setattr(file_id_obj, "mime_type", getattr(media, "mime_type", ""))
    setattr(file_id_obj, "file_name", getattr(media, "file_name", ""))
    setattr(file_id_obj, "unique_id", file_unique_id)

    return file_id_obj


def get_media_from_message(message: Message) -> Optional[Any]:
    """Return the media object from a message if present."""
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
    """Return the first 6 characters of a media's unique ID as a hash."""
    media = get_media_from_message(message)
    return getattr(media, "file_unique_id", "")[:6]


def get_name(message: Message) -> str:
    """Return the file name of a media message."""
    media = get_media_from_message(message)
    return getattr(media, "file_name", "")


def get_media_file_size(message: Message) -> int:
    """Return the size of the media in bytes."""
    media = get_media_from_message(message)
    return getattr(media, "file_size", 0)
