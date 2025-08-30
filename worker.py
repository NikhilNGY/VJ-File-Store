import os

# Base folder
base_dir = "TechVJ"

# Folder structure
folders = [
    base_dir,
    os.path.join(base_dir, "bot"),
    os.path.join(base_dir, "utils")
]

# Files with their content
files = {
    os.path.join(base_dir, "__init__.py"): '''from datetime import datetime

StartTime = datetime.utcnow()
__version__ = "1.0.0"
''',

    os.path.join(base_dir, "config.py"): '''import os

API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
''',

    os.path.join(base_dir, "start.py"): '''import asyncio
from bot.Bot import Bot

async def main():
    bot = Bot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
''',

    os.path.join(base_dir, "bot", "__init__.py"): '''from .Bot import Bot
from .multi_clients import *
from .work_loads import *
from .StreamBot import *
from .Script import script
''',

    os.path.join(base_dir, "bot", "Bot.py"): '''from .Script import script

class Bot:
    def __init__(self):
        self.name = "TechVJ Bot"

    async def start(self):
        print(f"{self.name} started")
        await self.run_script()

    async def run_script(self):
        result = script()
        print("Script output:", result)
''',

    os.path.join(base_dir, "bot", "Script.py"): '''def script():
    return "Script is running"
''',

    os.path.join(base_dir, "bot", "multi_clients.py"): '''async def start():
    print("multi_clients started")
''',

    os.path.join(base_dir, "bot", "work_loads.py"): '''async def start():
    print("work_loads started")
''',

    os.path.join(base_dir, "bot", "StreamBot.py"): '''async def run():
    print("StreamBot running")
''',

    os.path.join(base_dir, "utils", "__init__.py"): '''# utils package
''',

    os.path.join(base_dir, "utils", "time_format.py"): '''def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"
''',

    os.path.join(base_dir, "utils", "custom_dl.py"): '''class ByteStreamer:
    def __init__(self, file_path):
        self.file_path = file_path

    def stream(self):
        try:
            with open(self.file_path, "rb") as f:
                while chunk := f.read(1024):
                    yield chunk
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.file_path} not found")
''',

    "Procfile": "worker: python3 -m TechVJ.start\n"
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for filepath, content in files.items():
    with open(filepath, "w") as f:
        f.write(content)

print(f"TechVJ worker repo created successfully in folder '{base_dir}'!")
