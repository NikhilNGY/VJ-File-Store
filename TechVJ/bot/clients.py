# (c) adarsh-goel

import asyncio
import logging
from typing import Dict, Optional, Tuple, AsyncIterator

from pyrogram import Client
from config import API_HASH, API_ID, MULTI_CLIENT, SLEEP_THRESHOLD
from TechVJ.utils.config_parser import TokenParser
from . import multi_clients, work_loads, StreamBot

logger = logging.getLogger(__name__)


class ClientManager:
    """Async context manager for handling multiple Pyrogram clients."""

    def __init__(self):
        self._clients: Dict[int, Client] = {}
        self._tokens: Dict[int, str] = TokenParser().parse_from_env()

    async def __aenter__(self) -> Dict[int, Client]:
        # Always include the default StreamBot
        self._clients[0] = StreamBot
        work_loads[0] = 0

        if not self._tokens:
            logger.info("No additional clients found, using default client.")
            multi_clients.update(self._clients)
            return multi_clients

        # Start additional clients concurrently
        clients_list = await asyncio.gather(
            *[self._start_client(client_id, token) for client_id, token in self._tokens.items()]
        )

        # Filter out None clients and update globals
        self._clients.update({cid: client for cid, client in clients_list if cid is not None})
        multi_clients.update(self._clients)

        # Enable multi-client mode if more than one client exists
        if len(self._clients) > 1:
            globals()['MULTI_CLIENT'] = True
            logger.info("Multi-Client Mode Enabled")
        else:
            logger.info("Using only default client")

        return multi_clients

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Gracefully stop all clients except the default StreamBot
        for client_id, client in self._clients.items():
            if client_id == 0:  # Skip default bot
                continue
            try:
                await client.stop()
                logger.info(f"Client {client_id} stopped gracefully")
            except Exception as e:
                logger.error(f"Error stopping client {client_id}: {e}", exc_info=True)

    async def _start_client(self, client_id: int, token: str) -> Optional[Tuple[int, Client]]:
        """Start a single Pyrogram client asynchronously."""
        try:
            logger.info(f"Starting Client {client_id}")
            if client_id == len(self._tokens):
                await asyncio.sleep(2)
                logger.info("This may take some time, please wait...")

            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=True
            ).start()

            work_loads[client_id] = 0
            return client_id, client
        except Exception as e:
            logger.error(f"Failed starting Client {client_id}: {e}", exc_info=True)
            return None
