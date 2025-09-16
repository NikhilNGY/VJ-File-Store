import logging
import asyncio
import random
import string
from datetime import date
import pytz
import aiohttp
from config import SHORTLINK_API, SHORTLINK_URL
from shortzy import Shortzy

# ---------------- Logger Setup ---------------- #
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------- Global Dictionaries ---------------- #
TOKENS = {}
VERIFIED = {}

# ---------------- Shorten Link Function ---------------- #
async def get_verify_shorted_link(link: str) -> str:
    """
    Shortens a given link using SHORTLINK_URL and SHORTLINK_API.
    If SHORTLINK_URL is api.shareus.io, uses direct API call via aiohttp.
    Otherwise, uses Shortzy library.
    """
    if SHORTLINK_URL.lower() == "api.shareus.io":
        url = f'https://{SHORTLINK_URL}/easy_api'
        params = {"key": SHORTLINK_API, "link": link}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, ssl=False) as response:
                    response.raise_for_status()
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(f"Error shortening link via shareus.io: {e}")
            return link
    else:
        try:
            shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
            shortened_link = await shortzy.convert(link)
            return shortened_link
        except Exception as e:
            logger.error(f"Error shortening link via Shortzy: {e}")
            return link

# ---------------- Token Check Function ---------------- #
async def check_token(bot, userid: int, token: str) -> bool:
    """
    Checks if a given token for a user exists and is unused.
    """
    try:
        user = await bot.get_users(userid)
        user_tokens = TOKENS.get(user.id, {})
        if token in user_tokens:
            return not user_tokens[token]  # True if unused, False if already used
        return False
    except Exception as e:
        logger.error(f"Error checking token for user {userid}: {e}")
        return False

# ---------------- Token Generation Function ---------------- #
async def get_token(bot, userid: int, link: str) -> str:
    """
    Generates a random token for a user and returns a shortened verification URL.
    """
    try:
        user = await bot.get_users(userid)
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        TOKENS[user.id] = {token: False}
        verification_link = f"{link}verify-{user.id}-{token}"
        shortened_verify_url = await get_verify_shorted_link(verification_link)
        return shortened_verify_url
    except Exception as e:
        logger.error(f"Error generating token for user {userid}: {e}")
        return link

# ---------------- User Verification Function ---------------- #
async def verify_user(bot, userid: int, token: str):
    """
    Marks a token as used and stores verification date for a user.
    """
    try:
        user = await bot.get_users(userid)
        TOKENS[user.id] = {token: True}
        today = date.today()
        VERIFIED[user.id] = str(today)
    except Exception as e:
        logger.error(f"Error verifying user {userid}: {e}")

# ---------------- Verification Check Function ---------------- #
async def check_verification(bot, userid: int) -> bool:
    """
    Checks if a user's verification is still valid.
    """
    try:
        user = await bot.get_users(userid)
        if user.id not in VERIFIED:
            return False

        exp_date_str = VERIFIED[user.id]
        year, month, day = map(int, exp_date_str.split('-'))
        comp_date = date(year, month, day)
        today = date.today()
        return comp_date >= today
    except Exception as e:
        logger.error(f"Error checking verification for user {userid}: {e}")
        return False