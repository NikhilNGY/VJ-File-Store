# TechVJ Bot - Modern Async Pyrogram Version
# (©) CodeXBotz

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from config import ADMINS, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

# Script.py

# Option 1: as a class
class script:
    def __init__(self):
        print("Script class initialized")

# Option 2: as a function
# def script():
#     print("Script function called")

# ======================== Constants ======================== #

START_TXT = (
    "Friends.......🖤 We have already lost many channels due to copyright... "
    "So join us by giving your support, cooperation and blessings to this new channel of ours 🙏🙏\n\n"
    "Team: @KR_Picture"
)

WAIT_MSG = "<b>Processing ...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without any spaces.</code>"
COPY_DELAY = 0.5  # Delay between message copies

# ======================== Helper Functions ======================== #

async def safe_copy(chat_id: int, msg: Message) -> str:
    """Copy a message safely with error handling."""
    try:
        await msg.copy(
            chat_id=chat_id,
            caption=msg.caption.html if msg.caption else "",
            parse_mode=ParseMode.HTML,
            reply_markup=None if DISABLE_CHANNEL_BUTTON else msg.reply_markup,
            protect_content=PROTECT_CONTENT
        )
        return "success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.copy(
            chat_id=chat_id,
            caption=msg.caption.html if msg.caption else "",
            parse_mode=ParseMode.HTML,
            reply_markup=None if DISABLE_CHANNEL_BUTTON else msg.reply_markup,
            protect_content=PROTECT_CONTENT
        )
        return "success"
    except UserIsBlocked:
        await del_user(chat_id)
        return "blocked"
    except InputUserDeactivated:
        await del_user(chat_id)
        return "deleted"
    except Exception:
        return "unsuccessful"

def build_start_keyboard() -> InlineKeyboardMarkup:
    """Return the default start inline keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴜᴩᴅᴀᴛꜱ", url="https://t.me/KR_Picture"),
            InlineKeyboardButton("ɢʀᴏᴜᴩ", url="https://t.me/+x6OfRDdUPrUwZTZl")
        ],
        [
            InlineKeyboardButton("Any Issue Contact", url="https://t.me/Nikhil5757h")
        ]
    ])

# ======================== Bot Commands ======================== #

@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message) -> None:
    """Handle /start command for subscribed users."""
    user_id = message.from_user.id

    # Add user to database if not present
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception:
            pass

    text = message.text
    if len(text) > 7:
        # Decode arguments from base64
        try:
            base64_string = text.split(" ", 1)[1]
            decoded_string = await decode(base64_string)
            arguments = decoded_string.split("-")
        except Exception:
            return

        ids = []
        try:
            if len(arguments) == 3:
                start = int(int(arguments[1]) / abs(client.db_channel.id))
                end = int(int(arguments[2]) / abs(client.db_channel.id))
                ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
            elif len(arguments) == 2:
                ids = [int(int(arguments[1]) / abs(client.db_channel.id))]
        except Exception:
            return

        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception:
            await temp_msg.edit("Something went wrong..!")
            return
        await temp_msg.delete()

        for msg in messages:
            # Prepare caption
            if CUSTOM_CAPTION and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name
                )
            else:
                caption = msg.caption.html if msg.caption else ""

            await safe_copy(user_id, msg)
            await asyncio.sleep(COPY_DELAY)
        return

    # Default start message
    await message.reply_text(
        text=START_TXT,
        reply_markup=build_start_keyboard()
    )

# ======================== Not Joined Handler ======================== #

@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message) -> None:
    """Handle /start command for users who haven't joined the required channel."""
    buttons = [[InlineKeyboardButton("Join Channel", url=client.invitelink)]]

    try:
        buttons.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

# ======================== Admin Commands ======================== #

@Bot.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def get_users(client: Client, message: Message) -> None:
    """Return total number of bot users."""
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(ADMINS))
async def send_broadcast(client: Client, message: Message) -> None:
    """Broadcast a message to all users."""
    if not message.reply_to_message:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
        return

    broadcast_msg = message.reply_to_message
    users = await full_userbase()

    total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0
    pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")

    for user_id in users:
        result = await safe_copy(user_id, broadcast_msg)
        total += 1
        if result == "success":
            successful += 1
        elif result == "blocked":
            blocked += 1
        elif result == "deleted":
            deleted += 1
        else:
            unsuccessful += 1

    status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

    await pls_wait.edit(status)
