import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from plugins.clone import mongo_db

# Cache: { user_id: { link: (short_url, expiry_time) } }
_short_link_cache: Dict[int, Dict[str, tuple]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour TTL for cached short links
HTTP_RETRIES = 3
RETRY_DELAY = 1  # seconds


async def get_short_link(user: Dict[str, Any], link: str) -> Optional[str]:
    """Get shortened link for a user with caching and retry logic."""
    user_id = user.get("user_id")
    if user_id:
        cached = _short_link_cache.get(user_id, {}).get(link)
        if cached:
            short_url, expiry = cached
            if datetime.utcnow() < expiry:
                return short_url
            else:
                # Expired cache
                _short_link_cache[user_id].pop(link)

    api_key = user.get("shortener_api")
    base_site = user.get("base_site")
    if not api_key or not base_site:
        return None

    url = f"https://{base_site}/api?api={api_key}&url={link}"

    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        short_url = data.get("shortenedUrl")
                        if user_id:
                            expiry_time = datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
                            _short_link_cache.setdefault(user_id, {})[link] = (short_url, expiry_time)
                        return short_url
        except Exception as e:
            print(f"[Attempt {attempt}] Error getting short link: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return None


async def get_user(user_id: int) -> Dict[str, Any]:
    """Fetch user from MongoDB or create if not exists."""
    user_id = int(user_id)
    user = await mongo_db.user.find_one({"user_id": user_id})
    if not user:
        res = {"user_id": user_id, "shortener_api": None, "base_site": None}
        await mongo_db.user.insert_one(res)
        user = await mongo_db.user.find_one({"user_id": user_id})
    return user


async def update_user_info(user_id: int, value: Dict[str, Any]) -> None:
    """Update user info in MongoDB and clear cache."""
    user_id = int(user_id)
    newvalues = {"$set": value}
    await mongo_db.user.update_one({"user_id": user_id}, newvalues)
    _short_link_cache.pop(user_id, None)  # Clear cached links for updated user
