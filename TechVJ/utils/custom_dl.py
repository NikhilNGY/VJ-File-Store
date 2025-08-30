import asyncio
import logging
from typing import Dict, Union, Optional

from pyrogram import Client, utils, raw
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.session import Session, Auth
from pyrogram.errors import AuthBytesInvalid
from TechVJ.server.exceptions import FileNotFound
from TechVJ.bot import work_loads
from .file_properties import get_file_ids
from config import LOG_CHANNEL


class ByteStreamer:
    def __init__(self, client: Client, max_concurrent: int = 5, clean_interval: int = 1800):
        """
        Async-safe ByteStreamer using semaphore for workload management.
        
        Args:
            client: Pyrogram Client instance.
            max_concurrent: Maximum concurrent streaming per client.
            clean_interval: Seconds between cache cleanup.
        """
        self.client: Client = client
        self.clean_timer: int = clean_interval
        self.cached_file_ids: Dict[int, FileId] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        asyncio.create_task(self._clean_cache())

    async def get_file_properties(self, message_id: int) -> FileId:
        """Return cached file properties or generate them if missing."""
        if message_id not in self.cached_file_ids:
            await self.generate_file_properties(message_id)
            logging.debug(f"Cached file properties for message ID {message_id}")
        return self.cached_file_ids[message_id]

    async def generate_file_properties(self, message_id: int) -> FileId:
        """Generate and cache file properties for a message."""
        file_id = await get_file_ids(self.client, LOG_CHANNEL, message_id)
        if not file_id:
            logging.debug(f"Message with ID {message_id} not found")
            raise FIleNotFound
        self.cached_file_ids[message_id] = file_id
        logging.debug(f"Cached media message with ID {message_id}")
        return file_id

    async def generate_media_session(self, file_id: FileId) -> Session:
        """Generate or reuse media session for a given file's DC."""
        media_session = self.client.media_sessions.get(file_id.dc_id)
        if media_session:
            logging.debug(f"Using cached media session for DC {file_id.dc_id}")
            return media_session

        if file_id.dc_id != await self.client.storage.dc_id():
            media_session = Session(
                self.client,
                file_id.dc_id,
                await Auth(self.client, file_id.dc_id, await self.client.storage.test_mode()).create(),
                await self.client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()
            for _ in range(6):
                exported_auth = await self.client.invoke(raw.functions.auth.ExportAuthorization(dc_id=file_id.dc_id))
                try:
                    await media_session.send(raw.functions.auth.ImportAuthorization(
                        id=exported_auth.id, bytes=exported_auth.bytes
                    ))
                    break
                except AuthBytesInvalid:
                    logging.debug(f"Invalid auth bytes for DC {file_id.dc_id}, retrying...")
                    continue
            else:
                await media_session.stop()
                raise AuthBytesInvalid
        else:
            media_session = Session(
                self.client,
                file_id.dc_id,
                await self.client.storage.auth_key(),
                await self.client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()

        logging.debug(f"Created media session for DC {file_id.dc_id}")
        self.client.media_sessions[file_id.dc_id] = media_session
        return media_session

    @staticmethod
    async def get_location(file_id: FileId) -> Union[
        raw.types.InputPhotoFileLocation,
        raw.types.InputDocumentFileLocation,
        raw.types.InputPeerPhotoFileLocation,
    ]:
        """Return the correct InputFileLocation object for the given FileId."""
        if file_id.file_type == FileType.CHAT_PHOTO:
            peer = await ByteStreamer._get_peer(file_id)
            return raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        elif file_id.file_type == FileType.PHOTO:
            return raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        return raw.types.InputDocumentFileLocation(
            id=file_id.media_id,
            access_hash=file_id.access_hash,
            file_reference=file_id.file_reference,
            thumb_size=file_id.thumbnail_size,
        )

    @staticmethod
    async def _get_peer(file_id: FileId):
        """Helper to determine peer for CHAT_PHOTO type."""
        if file_id.chat_id > 0:
            return raw.types.InputPeerUser(user_id=file_id.chat_id, access_hash=file_id.chat_access_hash)
        if file_id.chat_access_hash == 0:
            return raw.types.InputPeerChat(chat_id=-file_id.chat_id)
        return raw.types.InputPeerChannel(
            channel_id=utils.get_channel_id(file_id.chat_id),
            access_hash=file_id.chat_access_hash,
        )

    async def yield_file(
        self,
        file_id: FileId,
        index: int,
        offset: int,
        first_part_cut: int,
        last_part_cut: int,
        part_count: int,
        chunk_size: int,
    ):
        """Yield file bytes from Telegram servers with concurrency control."""
        async with self.semaphore:
            work_loads[index] += 1
            logging.debug(f"Starting to yield file with client {index}")
            media_session = await self.generate_media_session(file_id)
            location = await self.get_location(file_id)
            current_part = 1

            try:
                r = await media_session.send(raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size))
                if not isinstance(r, raw.types.upload.File):
                    return

                while True:
                    chunk = r.bytes
                    if not chunk:
                        break

                    if part_count == 1:
                        yield chunk[first_part_cut:last_part_cut]
                    elif current_part == 1:
                        yield chunk[first_part_cut:]
                    elif current_part == part_count:
                        yield chunk[:last_part_cut]
                    else:
                        yield chunk

                    current_part += 1
                    offset += chunk_size
                    if current_part > part_count:
                        break

                    r = await media_session.send(raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size))
            finally:
                logging.debug(f"Finished yielding file, {current_part} parts processed")
                work_loads[index] -= 1

    async def _clean_cache(self):
        """Periodically clears the cached file IDs to save memory."""
        while True:
            await asyncio.sleep(self.clean_timer)
            self.cached_file_ids.clear()
            logging.debug("Cleared cached file properties")
