import logging, asyncio, random, string
from datetime import datetime, timedelta
import pytz, aiohttp
from config import SHORTLINK_API, SHORTLINK_URL
from shortzy import Shortzy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Stores tokens: { user_id: { token: {"used": bool, "created_at": datetime} } }
TOKENS = {}

# Stores verified users: { user_id: verification_datetime }
VERIFIED = {}

# Timezone
TZ = pytz.timezone("Asia/Kolkata")

TOKEN_EXPIRY_HOURS = 24
CLEANUP_INTERVAL_MINUTES = 60  # Cleanup every 60 minutes

async def get_verify_shorted_link(link: str) -> str:
    """Generate a shortened link using configured shortlink service."""
    if SHORTLINK_URL == "api.shareus.io":
        url = f"https://{SHORTLINK_URL}/easy_api"
        params = {"key": SHORTLINK_API, "link": link}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, ssl=False) as response:
                    response.raise_for_status()
                    return await response.text()
        except Exception as e:
            logger.error(f"Shortlink error: {e}")
            return link
    else:
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        return await shortzy.convert(link)

async def check_token(bot, userid: int, token: str) -> bool:
    """Check if the token exists, is unused, and not expired (24h)."""
    user = await bot.get_users(userid)
    user_tokens = TOKENS.get(user.id, {})
    token_data = user_tokens.get(token)
    if not token_data:
        return False

    if token_data["used"]:
        return False

    if datetime.now(TZ) - token_data["created_at"] > timedelta(hours=TOKEN_EXPIRY_HOURS):
        del user_tokens[token]
        return False

    return True

async def get_token(bot, userid: int, link: str) -> str:
    """Generate a verification token and return a shortened verify link."""
    user = await bot.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS.setdefault(user.id, {})[token] = {
        "used": False,
        "created_at": datetime.now(TZ)
    }
    verify_link = f"{link}verify-{user.id}-{token}"
    return await get_verify_shorted_link(verify_link)

async def verify_user(bot, userid: int, token: str) -> None:
    """Mark token as used and record user verification datetime."""
    user = await bot.get_users(userid)
    user_tokens = TOKENS.get(user.id, {})
    if token in user_tokens:
        user_tokens[token]["used"] = True

    VERIFIED[user.id] = datetime.now(TZ)

async def check_verification(bot, userid: int) -> bool:
    """Check if the user has a valid verification (within 24h)."""
    user = await bot.get_users(userid)
    verified_at = VERIFIED.get(user.id)
    if not verified_at:
        return False

    if datetime.now(TZ) - verified_at > timedelta(hours=TOKEN_EXPIRY_HOURS):
        del VERIFIED[user.id]
        return False

    return True

async def cleanup_expired_data():
    """Remove expired tokens and verifications periodically."""
    while True:
        now = datetime.now(TZ)

        # Cleanup tokens
        for user_id, tokens in list(TOKENS.items()):
            for token, data in list(tokens.items()):
                if now - data["created_at"] > timedelta(hours=TOKEN_EXPIRY_HOURS):
                    del tokens[token]
            if not tokens:
                del TOKENS[user_id]

        # Cleanup verified users
        for user_id, verified_at in list(VERIFIED.items()):
            if now - verified_at > timedelta(hours=TOKEN_EXPIRY_HOURS):
                del VERIFIED[user_id]

        await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)

async def start_cleanup_task():
    """Start the cleanup task in the background."""
    asyncio.create_task(cleanup_expired_data())
