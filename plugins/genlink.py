# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @KR_Picture
# Ask Doubt on telegram @KingVJ01

import re
import os
import json
import base64
from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link

# ---------------------- Utility ---------------------- #
async def allowed(_, __, message):
    """Check if the user is allowed to use the bot."""
    return PUBLIC_FILE_STORE or (message.from_user and message.from_user.id in ADMINS)

async def generate_share_link(bot, message_id: int, prefix: str = "file_") -> str:
    """Generate base64 encoded share link."""
    string = f"{prefix}{message_id}"
    return base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

async def build_final_link(bot, user_id, encoded_id, is_batch=False):
    """Build final share link, optionally shortened."""
    username = (await bot.get_me()).username
    user = await get_user(user_id)
    prefix = "BATCH-" if is_batch else ""
    
    share_link = f"{WEBSITE_URL}?KR_Picture={prefix}{encoded_id}" if WEBSITE_URL_MODE else f"https://t.me/{username}?start={prefix}{encoded_id}"
    
    if user.get("base_site") and user.get("shortener_api"):
        try:
            short_link = await get_short_link(user, share_link)
            return short_link
        except Exception:
            return share_link
    return share_link

# ---------------------- Single File Link ---------------------- #
@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    post = await message.copy(LOG_CHANNEL)
    encoded_id = await generate_share_link(bot, post.id)
    user_id = message.from_user.id
    final_link = await build_final_link(bot, user_id, encoded_id)
    
    await message.reply(f"<b>⭕ Here is your link:\n\n🔗 {final_link}</b>")

@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_reply(bot, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to get a shareable link.")
    
    post = await message.reply_to_message.copy(LOG_CHANNEL)
    encoded_id = await generate_share_link(bot, post.id)
    user_id = message.from_user.id
    final_link = await build_final_link(bot, user_id, encoded_id)
    
    await message.reply(f"<b>⭕ Here is your link:\n\n🔗 {final_link}</b>")

# ---------------------- Batch Mode ---------------------- #
@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    text = message.text.strip().split()
    if len(text) != 3:
        return await message.reply("Use correct format.\nExample: /batch https://t.me/channel/10 https://t.me/channel/20")
    
    _, first, last = text
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[\w_]+)/(\d+)$")
    
    def parse_link(link):
        match = regex.match(link)
        if not match:
            return None, None
        chat_id, msg_id = match.group(4), int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
        return chat_id, msg_id
    
    f_chat_id, f_msg_id = parse_link(first)
    l_chat_id, l_msg_id = parse_link(last)
    if None in [f_chat_id, l_chat_id] or f_chat_id != l_chat_id:
        return await message.reply("Invalid or mismatched chat links.")
    
    try:
        await bot.get_chat(f_chat_id)
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified):
        return await message.reply("Cannot access the channel/group. Make sure I'm admin.")
    except Exception as e:
        return await message.reply(f"Error: {e}")

    sts = await message.reply("**Generating links. This may take a while...**")
    outlist = []
    count = 0

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        if msg.empty or msg.service:
            continue
        outlist.append({"channel_id": f_chat_id, "msg_id": msg.id})
        count += 1
        if count % 20 == 0:
            try:
                await sts.edit(f"Processed {count} messages...")
            except:
                pass
    
    filename = f"batch_{message.from_user.id}.json"
    with open(filename, "w+") as f:
        json.dump(outlist, f)
    
    post = await bot.send_document(LOG_CHANNEL, filename, file_name="Batch.json", caption="⚠️ Batch Generated for Filestore.")
    os.remove(filename)
    
    encoded_id = await generate_share_link(bot, post.id, prefix="BATCH-")
    final_link = await build_final_link(bot, message.from_user.id, encoded_id, is_batch=True)
    await sts.edit(f"<b>⭕ Here is your batch link:\n\nContains `{count}` files.\n\n🔗 {final_link}</b>")
