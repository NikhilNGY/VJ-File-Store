# TechVJ/server/__init__.py
import asyncio
import logging
import os
import signal
from aiohttp import web
from .stream_routes import routes
from TechVJ.bot import multi_clients, work_loads
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_app() -> web.Application:
    """
    Initialize aiohttp app with routes and shared resources.
    """
    app = web.Application(client_max_size=30 * 1024 * 1024)
    app.add_routes(routes)

    # Shared cache for ByteStreamer objects
    app["streamer_cache"] = {}

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

async def on_startup(app: web.Application):
    logger.info("Starting TechVJ web server...")

async def on_cleanup(app: web.Application):
    logger.info("Cleaning up resources...")
    # Close all multi_clients connections if needed
    for client in multi_clients:
        try:
            await client.disconnect()
        except Exception:
            pass

async def run_server(host: str = "0.0.0.0", port: int = 8080):
    """
    Run the aiohttp web server with graceful shutdown.
    """
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    logger.info(f"Server running at http://{host}:{port}")

    shutdown_event = asyncio.Event()

    def stop_server():
        logger.info("Shutdown signal received. Stopping server...")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_server)

    await shutdown_event.wait()
    await runner.cleanup()
    logger.info("Server successfully stopped.")

def watch_and_reload():
    """
    Watch the server directory for changes and restart the process.
    """
    server_dir = Path(__file__).parent
    logger.info(f"Watching {server_dir} for changes...")

    try:
        import watchgod
    except ImportError:
        logger.warning("watchgod not installed, hot-reload disabled.")
        return

    while True:
        changes = watchgod.watch(server_dir)
        for change_type, path in changes:
            logger.info(f"File changed: {path}. Restarting server...")
            python = os.sys.executable
            os.execv(python, [python] + os.sys.argv)

if __name__ == "__main__":
    if os.getenv("DEV_RELOAD") == "1":
        watch_and_reload()
    else:
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            logger.info("Server interrupted by user.")
