import asyncio
from TechVJ.bot import StreamBot, multi_clients, work_loads

async def main():
    # Initialize and start your bot
    await multi_clients.start()
    await work_loads.start()
    await StreamBot.run()

if __name__ == "__main__":
    asyncio.run(main())
