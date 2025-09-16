# t.me/Nikhil5757h 

import sys
import glob
import importlib
from pathlib import Path
import logging
import logging.config
from pyrogram import idle
from pyrogram import Client, __version__
from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web
from TechVJ.server import web_server
import asyncio
from plugins.clone import restart_bots
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# Logging configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

ppath = "plugins/*.py"
files = glob.glob(ppath)

async def start():
    print('\n')
    print('Initializing Tech VJ Bot')

    # Start the StreamBot
    await StreamBot.start()

    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username

    await initialize_clients()

    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")

    app = web.AppRunner(await web_server())
    await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time_str))
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()

    if CLONE_MODE:
        await restart_bots()

    print("Bot Started Powered By @VJ_Botz")

    await idle()
    await StreamBot.stop()

if __name__ == '__main__':
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')