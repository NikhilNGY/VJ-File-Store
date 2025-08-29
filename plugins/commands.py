# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@KR_Picture
# Ask Doubt on telegram @KingVJ01

import os
import logging
import random
import asyncio
import json
import base64
from urllib.parse import quote_plus

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo, Message, CallbackQuery
from pyrogram.errors import FloodWait
from validators import domain

from Script import script
from plugins.dbusers import db
from plugins.users_api import get_user, update_user_info
from utils import verify_user, check_token, check_verification, get_token
from config import *
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
BATCH_FILES = {}

# -------------------- Helper Functions --------------------

def get_size(size: int) -> str:
    """Convert size in bytes to a readable format."""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    i = 0
    size = float(size)
    while size >= 1024 and i < len(units)-1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"

def format_file_name(file_name: str) -> str:
    """Clean and format file names for messages."""
    for c in ["[", "]", "(", ")"]:
        file_name = file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(filter(lambda x: not x.startswith(('http', '@', 'www.')), file_name.split()))
    return file_name

async def send_start_buttons(client: Client, message: Message):
    """Send start message with buttons."""
    username = client.me.username
    buttons = [
        [InlineKeyboardButton('💝 Subscribe YouTube Channel', url='https://youtube.com/@KR_Picture')],
        [InlineKeyboardButton('🔍 Support Group', url='https://t.me/vj_bot_disscussion'),
         InlineKeyboardButton('🤖 Update Channel', url='https://t.me/vj_botz')],
        [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
         InlineKeyboardButton('😊 About', callback_data='about')]
    ]
    if CLONE_MODE:
        buttons.append([InlineKeyboardButton('🤖 Create your own clone bot', callback_data='clone')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.START_TXT.format(message.from_user.mention, (await client.get_me()).mention),
        reply_markup=reply_markup
    )

async def handle_auto_delete(client: Client, files_arr: list[Message]):
    """Automatically delete sent messages after AUTO_DELETE_TIME."""
    if AUTO_DELETE_MODE:
        k = await client.send_message(
            chat_id=files_arr[0].chat.id,
            text=f"<b><u>❗️❗️IMPORTANT❗️❗️</u></b>\n\n"
                 f"This file/video will be deleted in <b><u>{AUTO_DELETE} minutes</u></b> "
                 f"(Due to Copyright Issues).\n\n"
                 f"<b>Please forward this file/video to your Saved Messages!</b>"
        )
        await asyncio.sleep(AUTO_DELETE_TIME)
        for x in files_arr:
            try: await x.delete()
            except: pass
        await k.edit_text("<b>Your files/videos have been successfully deleted!</b>")

# -------------------- Command Handlers --------------------

@Client.on_message(filters.command("start") & filters.incoming)
async def start_handler(client: Client, message: Message):
    username = client.me.username

    # Add new user
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))

    # Start without arguments
    if len(message.command) != 2:
        return await send_start_buttons(client, message)

    data = message.command[1]
    # Handle verification links
    if data.startswith("verify-"):
        userid, token = data.split("-")[1:3]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text("<b>Invalid link or expired link!</b>", protect_content=True)
        if await check_token(client, userid, token):
            await message.reply_text(
                f"<b>Hey {message.from_user.mention}, you are successfully verified! "
                f"Now you have unlimited access for all files till today midnight.</b>", protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            await message.reply_text("<b>Invalid link or expired link!</b>", protect_content=True)
        return

    # Handle batch files
    if data.startswith("BATCH-"):
        if VERIFY_MODE and not await check_verification(client, message.from_user.id):
            btn = [[InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))],
                   [InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)]]
            return await message.reply_text(
                "<b>You are not verified! Kindly verify to continue!</b>",
                protect_content=True, reply_markup=InlineKeyboardMarkup(btn)
            )

        sts = await message.reply("**🔺 Please wait...**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            media = getattr(msg, msg.media.value)
            file = await client.download_media(media.file_id)
            try:
                with open(file) as f:
                    msgs = json.load(f)
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs

        files_arr = []
        for msg_data in msgs:
            try:
                info = await client.get_messages(int(msg_data["channel_id"]), int(msg_data["msg_id"]))
                file_msg = await info.copy(chat_id=message.from_user.id, protect_content=False)
                files_arr.append(file_msg)
                await asyncio.sleep(1)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except:
                continue

        await handle_auto_delete(client, files_arr)
        await sts.delete()
        return

# -------------------- Shortener & Base Site Commands --------------------

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    cmd = message.command

    if len(cmd) == 1:
        await message.reply(script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"]))
    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await message.reply(f"<b>Shortener API updated successfully to</b> {api}")

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client: Client, message: Message):
    user_id = message.from_user.id
    cmd = message.command
    help_text = f"`/base_site (base_site)`\n\n<b>Current base site: None\n\n EX:</b> `/base_site shortnerdomain.com`\n\nSend `/base_site None` to remove base site"
    if len(cmd) == 1:
        return await message.reply(help_text, disable_web_page_preview=True)
    base_site = cmd[1].strip()
    if base_site.lower() == "none":
        await update_user_info(user_id, {"base_site": None})
        return await message.reply("<b>Base Site removed successfully</b>")
    if not domain(base_site):
        return await message.reply(help_text, disable_web_page_preview=True)
    await update_user_info(user_id, {"base_site": base_site})
    await message.reply("<b>Base Site updated successfully</b>")

# -------------------- Callback Queries --------------------

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    query_data = query.data
    if query_data == "close_data":
        await query.message.delete()
        return
    elif query_data in ["about", "start", "clone", "help"]:
        buttons_map = {
            "start": [[InlineKeyboardButton('💝 Subscribe YouTube Channel', url='https://youtube.com/@KR_Picture')],
                      [InlineKeyboardButton('🔍 Support Group', url='https://t.me/vj_bot_disscussion'),
                       InlineKeyboardButton('🤖 Update Channel', url='https://t.me/vj_botz')],
                      [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                       InlineKeyboardButton('😊 About', callback_data='about')]],
            "about": [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
                       InlineKeyboardButton('🔒 Close', callback_data='close_data')]],
            "clone": [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
                       InlineKeyboardButton('🔒 Close', callback_data='close_data')]],
            "help": [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
                      InlineKeyboardButton('🔒 Close', callback_data='close_data')]]
        }
        buttons = buttons_map[query_data]
        await client.edit_message_media(query.message.chat.id, query.message.id, InputMediaPhoto(random.choice(PICS)))
        await query.message.edit_text(
            text=script.__dict__.get(f"{query_data.upper()}_TXT", ""),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
