import os
import logging
import random
import asyncio
import json
import base64
from urllib.parse import quote_plus
from validators import domain

from pyrogram import Client, filters, enums
from pyrogram.types import *
from pyrogram.errors import FloodWait, ChatAdminRequired

from Script import script
from plugins.dbusers import db
from plugins.users_api import get_user, update_user_info
from utils import verify_user, check_token, check_verification, get_token
from config import *
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)

BATCH_FILES = {}

# ---------------- UTILITY FUNCTIONS ---------------- #

def get_size(size):
    """Convert file size to human-readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return "%.2f %s" % (size, units[i])


def formate_file_name(file_name):
    """Format file name by removing unwanted characters and prefix"""
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name = file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(
        filter(lambda x: not x.startswith(('http', '@', 'www.')), file_name.split())
    )
    return file_name

# ---------------- START COMMAND ---------------- #

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    username = client.me.username
    user_id = message.from_user.id

    # Add user to DB if new
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(user_id, message.from_user.mention))

    # Default start menu
    if len(message.command) != 2:
        buttons = [
            [InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')],
            [
                InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
                InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
            ],
            [
                InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
            ]
        ]
        if CLONE_MODE:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])

        reply_markup = InlineKeyboardMarkup(buttons)
        me = client.me
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, me.mention),
            reply_markup=reply_markup
        )
        return

    # Handling deep link / batch / verification
    data = message.command[1]

    try:
        pre, file_id = data.split('_', 1)
    except ValueError:
        file_id = data
        pre = ""

    # ---------------- VERIFICATION LINK ---------------- #
    if data.startswith("verify-"):
        parts = data.split("-")
        userid, token = parts[1], parts[2]
        if str(user_id) != userid:
            return await message.reply_text("<b>Invalid link or Expired link !</b>", protect_content=True)
        is_valid = await check_token(client, userid, token)
        if is_valid:
            await message.reply_text(
                f"<b>Hey {message.from_user.mention}, You are successfully verified!\n"
                f"Now you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            await message.reply_text("<b>Invalid link or Expired link !</b>", protect_content=True)
        return

    # ---------------- BATCH FILES ---------------- #
    if data.startswith("BATCH-"):
        try:
            if VERIFY_MODE and not await check_verification(client, user_id):
                btn = [
                    [InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://telegram.me/{username}?start="))],
                    [InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)]
                ]
                await message.reply_text(
                    "<b>You are not verified!\nKindly verify to continue!</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            return await message.reply_text(f"**Error - {e}**")

        sts = await message.reply("**🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)

        if not msgs:
            decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            media = getattr(msg, msg.media.value)
            file_id = media.file_id
            file_path = await client.download_media(file_id)
            try:
                with open(file_path, "r") as file_data:
                    msgs = json.load(file_data)
            except Exception as e:
                await sts.edit("FAILED")
                await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                return
            os.remove(file_path)
            BATCH_FILES[file_id] = msgs

        filesarr = []
        for msg_data in msgs:
            channel_id = int(msg_data.get("channel_id"))
            msg_id = int(msg_data.get("msg_id"))
            info = await client.get_messages(channel_id, msg_id)

            if info.media:
                file_attr = getattr(info, info.media.value)
                f_caption = getattr(info, 'caption', '')
                f_caption = getattr(f_caption, 'html', f_caption) if f_caption else ''

                old_title = getattr(file_attr, "file_name", "")
                title = formate_file_name(old_title)
                size = get_size(getattr(file_attr, "file_size", 0))

                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(
                            file_name=title or "",
                            file_size=size or "",
                            file_caption=f_caption or ""
                        )
                    except:
                        pass
                if f_caption is None:
                    f_caption = f"{title}"

                reply_markup = None
                if STREAM_MODE and (info.video or info.document):
                    stream_url = f"{URL}watch/{info.id}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                    download_url = f"{URL}{info.id}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                    button = [
                        [InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download_url),
                         InlineKeyboardButton("• ᴡᴀᴛᴄʜ •", url=stream_url)],
                        [InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream_url))]
                    ]
                    reply_markup = InlineKeyboardMarkup(button)

                try:
                    sent_msg = await info.copy(
                        chat_id=user_id,
                        caption=f_caption,
                        protect_content=False,
                        reply_markup=reply_markup
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    sent_msg = await info.copy(
                        chat_id=user_id,
                        caption=f_caption,
                        protect_content=False,
                        reply_markup=reply_markup
                    )
                except Exception:
                    continue
            else:
                try:
                    sent_msg = await info.copy(chat_id=user_id, protect_content=False)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    sent_msg = await info.copy(chat_id=user_id, protect_content=False)
                except Exception:
                    continue

            filesarr.append(sent_msg)
            await asyncio.sleep(1)

        await sts.delete()

        # Auto delete mode
        if AUTO_DELETE_MODE:
            notice_msg = await client.send_message(
                chat_id=user_id,
                text=f"<b><u>❗️❗️❗️IMPORTANT❗️❗️❗️</u></b>\n\n"
                     f"This Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u></b> 🫥 "
                     f"<i>(Due to Copyright Issues)</i>.\n\n"
                     f"<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>"
            )
            await asyncio.sleep(AUTO_DELETE_TIME)
            for x in filesarr:
                try:
                    await x.delete()
                except:
                    pass
            await notice_msg.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")

# ---------------- API HANDLER ---------------- #

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(
            base_site=user.get("base_site", "None"),
            shortener_api=user.get("shortener_api", "None")
        )
        return await m.reply(s)

    elif len(cmd) == 2:
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply(f"<b>Shortener API updated successfully to</b> {api}")


# ---------------- BASE SITE HANDLER ---------------- #

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    default_text = (
        "/base_site (base_site)\n\n"
        "<b>Current base site: None\n\n EX:</b> /base_site shortnerdomain.com\n\n"
        "If You Want To Remove Base Site Then Copy This And Send To Bot - /base_site None"
    )

    if len(cmd) == 1:
        return await m.reply(text=default_text, disable_web_page_preview=True)

    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if base_site.lower() == "none":
            await update_user_info(user_id, {"base_site": None})
            return await m.reply("<b>Base Site removed successfully</b>")

        if not domain(base_site):
            return await m.reply(text=default_text, disable_web_page_preview=True)

        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("<b>Base Site updated successfully</b>")


# ---------------- CALLBACK QUERY HANDLER ---------------- #

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "close_data":
        await query.message.delete()

    elif data == "about":
        buttons = [
            [InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
             InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]
        ]
        await client.edit_message_media(query.message.chat.id, query.message.id,
                                        InputMediaPhoto(random.choice(PICS)))
        reply_markup = InlineKeyboardMarkup(buttons)
        me = (await client.get_me()).mention
        await query.message.edit_text(script.ABOUT_TXT.format(me), reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)

    elif data == "start":
        buttons = [
            [InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')],
            [InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
             InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')],
            [InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')]
        ]
        if CLONE_MODE:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])

        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(query.message.chat.id, query.message.id, InputMediaPhoto(random.choice(PICS)))
        me = (await client.get_me()).mention
        await query.message.edit_text(script.START_TXT.format(query.from_user.mention, me), reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)

    elif data == "clone":
        buttons = [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
                    InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]]
        await client.edit_message_media(query.message.chat.id, query.message.id, InputMediaPhoto(random.choice(PICS)))
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(script.CLONE_TXT.format(query.from_user.mention), reply_markup=reply_markup,
                                      parse_mode=enums.ParseMode.HTML)

    elif data == "help":
        buttons = [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
                    InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]]
        await client.edit_message_media(query.message.chat.id, query.message.id, InputMediaPhoto(random.choice(PICS)))
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(script.HELP_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)