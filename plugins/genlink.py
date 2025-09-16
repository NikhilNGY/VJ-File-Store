import re
import os
import json
import base64
import logging
from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified, FloodWait
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import asyncio

# ---------------- Setup logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- Permission Check ----------------
async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# ---------------- Single File Link ----------------
@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    try:
        username = (await bot.get_me()).username
        post = await message.copy(LOG_CHANNEL)
        file_id = str(post.id)
        encoded_id = base64.urlsafe_b64encode(f"file_{file_id}".encode("ascii")).decode().strip("=")
        user = await get_user(message.from_user.id)

        if WEBSITE_URL_MODE:
            share_link = f"{WEBSITE_URL}?start={encoded_id}"
        else:
            share_link = f"https://t.me/{username}?start={encoded_id}"

        if user.get("base_site") and user.get("shortener_api"):
            short_link = await get_short_link(user, share_link)
            await message.reply(f"<b>⭕ Here is your link:\n\n🖇️ Short Link: {short_link}</b>")
        else:
            await message.reply(f"<b>⭕ Here is your link:\n\n🔗 Original Link: {share_link}</b>")

    except Exception as e:
        logging.error(f"[incoming_gen_link] Error: {e}")
        await message.reply(f"⚠️ Failed to generate link: {e}")

# ---------------- Reply to Message Link ----------------
@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    try:
        username = (await bot.get_me()).username
        replied = message.reply_to_message
        if not replied:
            return await message.reply("Reply to a message to get a shareable link.")

        post = await replied.copy(LOG_CHANNEL)
        file_id = str(post.id)
        encoded_id = base64.urlsafe_b64encode(f"file_{file_id}".encode("ascii")).decode().strip("=")
        user = await get_user(message.from_user.id)

        if WEBSITE_URL_MODE:
            share_link = f"{WEBSITE_URL}?start={encoded_id}"
        else:
            share_link = f"https://t.me/{username}?start={encoded_id}"

        if user.get("base_site") and user.get("shortener_api"):
            short_link = await get_short_link(user, share_link)
            await message.reply(f"<b>⭕ Here is your link:\n\n🖇️ Short Link: {short_link}</b>")
        else:
            await message.reply(f"<b>⭕ Here is your link:\n\n🔗 Original Link: {share_link}</b>")

    except Exception as e:
        logging.error(f"[gen_link_s] Error: {e}")
        await message.reply(f"⚠️ Failed to generate link: {e}")

# ---------------- Batch Links ----------------
@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    try:
        username = (await bot.get_me()).username
        parts = message.text.strip().split(" ")
        if len(parts) != 3:
            return await message.reply("Use correct format:\n/batch <first_link> <last_link>")

        cmd, first, last = parts
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

        match_f = regex.match(first)
        match_l = regex.match(last)

        if not match_f or not match_l:
            return await message.reply("Invalid link(s) provided.")

        f_chat_id, f_msg_id = match_f.group(4), int(match_f.group(5))
        l_chat_id, l_msg_id = match_l.group(4), int(match_l.group(5))

        if f_chat_id.isnumeric():
            f_chat_id = int("-100" + f_chat_id)
        if l_chat_id.isnumeric():
            l_chat_id = int("-100" + l_chat_id)

        if f_chat_id != l_chat_id:
            return await message.reply("Chat IDs do not match.")

        try:
            await bot.get_chat(f_chat_id)
        except (ChannelInvalid, UsernameInvalid, UsernameNotModified) as e:
            return await message.reply(f"Cannot access channel/group: {e}")

        sts = await message.reply("**Generating batch links...** This may take some time.")

        outlist = []
        og_msg = 0
        total_msgs = l_msg_id - f_msg_id + 1

        async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
            if msg.empty or msg.service:
                continue
            outlist.append({"channel_id": f_chat_id, "msg_id": msg.id})
            og_msg += 1

            if og_msg % 20 == 0:
                try:
                    await sts.edit(f"Processing {og_msg}/{total_msgs} messages...")
                except:
                    pass

        json_file = f"batchmode_{message.from_user.id}.json"
        with open(json_file, "w") as f:
            json.dump(outlist, f)

        post = await bot.send_document(LOG_CHANNEL, json_file, file_name="Batch.json",
                                       caption=f"⚠️ Batch Generated for Filestore ({og_msg} files).")
        os.remove(json_file)

        file_id = base64.urlsafe_b64encode(str(post.id).encode("ascii")).decode().strip("=")
        user = await get_user(message.from_user.id)
        if WEBSITE_URL_MODE:
            share_link = f"{WEBSITE_URL}?start=BATCH-{file_id}"
        else:
            share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

        if user.get("base_site") and user.get("shortener_api"):
            short_link = await get_short_link(user, share_link)
            await sts.edit(f"<b>⭕ Batch link ready:\n\n🖇️ Short Link: {short_link}</b>")
        else:
            await sts.edit(f"<b>⭕ Batch link ready:\n\n🔗 Original Link: {share_link}</b>")

    except Exception as e:
        logging.error(f"[gen_link_batch] Error: {e}")
        await message.reply(f"⚠️ Failed to generate batch link: {e}")