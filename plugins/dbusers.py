# Don't Remove Credit Tg - @KR_Picture
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@KR_Picture
# Ask Doubt on telegram @KR_Picture

import aiohttp
from plugins.dbusers import db

async def get_short_link(user: dict, link: str) -> str | None:
    """
    Generate a shortened URL using user's shortener API.
    
    :param user: dict containing 'shortener_api' and 'base_site'
    :param link: original URL to shorten
    :return: shortened URL if success else None
    """
    api_key = user.get("shortener_api")
    base_site = user.get("base_site")

    if not api_key or not base_site:
        return None

    url = f"https://{base_site}/api?api={api_key}&url={link}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None

async def get_user(user_id: int) -> dict:
    """
    Fetch a user from the database; create if not exists.
    
    :param user_id: Telegram user ID
    :return: user dictionary
    """
    user_id = int(user_id)
    user = await db.users_collection.find_one({"id": user_id})

    if not user:
        new_user = {"id": user_id, "shortener_api": None, "base_site": None, "name": None}
        await db.users_collection.insert_one(new_user)
        user = new_user

    return user

async def update_user_info(user_id: int, values: dict) -> None:
    """
    Update user information in the database.

    :param user_id: Telegram user ID
    :param values: dictionary with fields to update
    """
    user_id = int(user_id)
    await db.users_collection.update_one({"id": user_id}, {"$set": values})
