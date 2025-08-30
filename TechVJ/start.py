# TechVJ/start.py
import asyncio
from aiohttp import web
from TechVJ.server import web_server
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    app = await web_server.web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    print("Server started on http://0.0.0.0:8080")
    await site.start()
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
