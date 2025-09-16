import os
import logging
import random
import asyncio
import json
import base64
from urllib.parse import quote_plus

from validators import domain
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *

from Script import script
from plugins.dbusers import db
from plugins.users_api import get_user, update_user_info
from utils import verify_user, check_token, check_verification, get_token
from config import *
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
BATCH_FILES = {}

# ---------------- Helper Functions ----------------
def get_size(size: int) -> str:
    """Convert file size to human-readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units)-1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

def format_file_name(file_name: str) -> str:
    """Clean file name and add credit"""
    for c in ["[", "]", "(", ")"]:
        file_name = file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(
        filter(lambda x: not x.startswith(('http','@','www.')), file_name.split())
    )
    return file_name

# ---------------- Start Command ----------------
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client: Client, message: Message):
    user_id = message.from_user.id
    username = client.me.username

    # Add user if not exist
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(user_id, message.from_user.mention))

    # No start parameter
    if len(message.command) == 1:
        buttons = [
            [InlineKeyboardButton('💝 Subscribe YouTube', url='https://youtube.com/@Tech_VJ')],
            [InlineKeyboardButton('🔍 Support Group', url='https://t.me/vj_bot_disscussion'),
             InlineKeyboardButton('🤖 Updates Channel', url='https://t.me/vj_botz')],
            [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
             InlineKeyboardButton('😊 About', callback_data='about')]
        ]
        if CLONE_MODE:
            buttons.append([InlineKeyboardButton('🤖 Create Your Own Clone Bot', callback_data='clone')])

        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, client.me.mention),
            reply_markup=reply_markup
        )
        return

    # Start parameter exists
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except ValueError:
        pre = ""
        file_id = data

    # ---------------- Verification ----------------
    if data.startswith("verify-"):
        parts = data.split("-")
        if str(message.from_user.id) != parts[1]:
            return await message.reply_text("<b>Invalid or expired link!</b>", protect_content=True)
        is_valid = await check_token(client, parts[1], parts[2])
        if is_valid:
            await verify_user(client, parts[1], parts[2])
            return await message.reply_text(f"<b>{message.from_user.mention}, verified successfully!</b>", protect_content=True)
        return await message.reply_text("<b>Invalid or expired link!</b>", protect_content=True)

    # ---------------- Batch File Handling ----------------
    if data.startswith("BATCH-"):
        if VERIFY_MODE and not await check_verification(client, user_id):
            btn = [
                [InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://t.me/{username}?start="))],
                [InlineKeyboardButton("How To Open & Verify", url=VERIFY_TUTORIAL)]
            ]
            return await message.reply_text(
                "<b>You are not verified! Kindly verify to continue.</b>",
                reply_markup=InlineKeyboardMarkup(btn), protect_content=True
            )

        sts = await message.reply("**🔺 Please wait...**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)

        # Load batch messages if not cached
        if not msgs:
            decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            media = getattr(msg, msg.media.value)
            downloaded_file = await client.download_media(media.file_id)
            try:
                with open(downloaded_file) as f:
                    msgs = json.load(f)
            except Exception:
                await sts.edit("Failed to read batch file.")
                return await client.send_message(LOG_CHANNEL, "Unable to open file.")
            finally:
                os.remove(downloaded_file)
            BATCH_FILES[file_id] = msgs

        # Send all files in batch
        files_arr = []
        for msg_info in msgs:
            try:
                channel_id, msg_id = int(msg_info["channel_id"]), msg_info["msg_id"]
                info = await client.get_messages(channel_id, int(msg_id))
                if info.media:
                    media_type = getattr(info, info.media.value)
                    title = format_file_name(getattr(media_type, "file_name", ""))
                    size = get_size(int(getattr(media_type, "file_size", 0)))
                    f_caption = getattr(info, 'caption', '')
                    if f_caption:
                        f_caption = f_caption.html
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption = BATCH_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption or '')
                        except:
                            pass

                    reply_markup = None
                    if STREAM_MODE and (info.video or info.document):
                        stream_url = f"{URL}watch/{info.id}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                        download_url = f"{URL}{info.id}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("• Download •", url=download_url),
                             InlineKeyboardButton("• Watch •", url=stream_url)],
                            [InlineKeyboardButton("• Watch in Web App •", web_app=WebAppInfo(url=stream_url))]
                        ])
                    try:
                        msg = await info.copy(
                            chat_id=user_id, caption=f_caption, protect_content=False, reply_markup=reply_markup
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        msg = await info.copy(chat_id=user_id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                    files_arr.append(msg)
                    await asyncio.sleep(1)
            except Exception:
                continue

        await sts.delete()

        # Auto delete files if enabled
        if AUTO_DELETE_MODE:
            notice = await client.send_message(
                chat_id=user_id,
                text=f"<b>❗️ IMPORTANT ❗️</b>\nThis file will be deleted in <b>{AUTO_DELETE} minutes</b> due to copyright issues."
            )
            await asyncio.sleep(AUTO_DELETE_TIME)
            for f in files_arr:
                try:
                    await f.delete()
                except Exception:
                    continue
            await notice.edit("<b>All files/videos have been successfully deleted!</b>")
        return

    # ---------------- Single File Handling ----------------
    if VERIFY_MODE and not await check_verification(client, user_id):
        btn = [
            [InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://t.me/{username}?start="))],
            [InlineKeyboardButton("How To Open & Verify", url=VERIFY_TUTORIAL)]
        ]
        return await message.reply_text(
            "<b>You are not verified! Kindly verify to continue.</b>",
            reply_markup=InlineKeyboardMarkup(btn), protect_content=True
        )

    try:
        decode_file_id = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("ascii").split("_", 1)[1]
        msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
        if msg.media:
            media = getattr(msg, msg.media.value)
            title = format_file_name(getattr(media, "file_name", ""))
            size = get_size(getattr(media, "file_size", 0))
            caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption='')
                except Exception:
                    pass
            reply_markup = None
            if STREAM_MODE and (msg.video or msg.document):
                stream_url = f"{URL}watch/{msg.id}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
                download_url = f"{URL}{msg.id}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• Download •", url=download_url),
                     InlineKeyboardButton("• Watch •", url=stream_url)],
                    [InlineKeyboardButton("• Watch in Web App •", web_app=WebAppInfo(url=stream_url))]
                ])
            del_msg = await msg.copy(chat_id=user_id, caption=caption, reply_markup=reply_markup, protect_content=False)
            if AUTO_DELETE_MODE:
                notice = await client.send_message(
                    chat_id=user_id,
                    text=f"<b>❗️ IMPORTANT ❗️</b>\nThis file will be deleted in <b>{AUTO_DELETE} minutes</b> due to copyright issues."
                )
                await asyncio.sleep(AUTO_DELETE_TIME)
                try:
                    await del_msg.delete()
                except Exception:
                    pass
                await notice