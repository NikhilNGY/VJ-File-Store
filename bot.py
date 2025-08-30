# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys
import glob
import importlib
from pathlib import Path
import logging
import logging.config
import asyncio
from datetime import date, datetime
from typing import List

import pytz
from aiohttp import web
from pyrogram import idle, Client
from pyrogram.raw.all import layer
from pyrogram import types

from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from TechVJ.Script import script
from TechVJ.server import web_server
from plugins.clone import restart_bots
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients


class Bot:
    def __init__(self):
        self.name = "TechVJ Bot"

    async def start(self):
        print(f"{self.name} started")
        await self.run_script()

    async def run_script(self):
        # Call the script function from Script.py
        result = script()
        print("Script output:", result)

# -------------------------
# Logging Configuration
# -------------------------
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# -------------------------
# Plugin Loader
# -------------------------
PLUGIN_PATH = "plugins/*.py"
plugin_files: List[str] = glob.glob(PLUGIN_PATH)

# -------------------------
# Bot Start
# -------------------------
StreamBot.start()
loop = asyncio.get_event_loop()


async def load_plugins() -> None:
    """Load all plugins dynamically."""
    for plugin_file in plugin_files:
        path = Path(plugin_file)
        plugin_name = path.stem
        module_path = Path(f"plugins/{plugin_name}.py")
        import_path = f"plugins.{plugin_name}"
        try:
            spec = importlib.util.spec_from_file_location(import_path, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            sys.modules[import_path] = module
            logger.info(f"Tech VJ Imported => {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")


async def start() -> None:
    """Start the bot with plugins, webserver, and optional clone/restart."""
    print("\nInitializing Tech VJ Bot...")

    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username

    await initialize_clients()
    await load_plugins()

    # Keep bot alive on Heroku
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Send startup message to log channel
    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S %p")

    try:
        app_runner = web.AppRunner(await web_server())
        await StreamBot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, current_time)
        )
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")

    # Restart bots if clone mode is enabled
    if CLONE_MODE:
        await restart_bots()

    print("Bot Started Powered By @VJ_Botz")
    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logger.info("Service Stopped Bye 👋")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
