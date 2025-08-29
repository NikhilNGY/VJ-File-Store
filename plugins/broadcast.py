# Don't Remove Credit Tg - @KR_Picture
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@KR_Picture
# Ask Doubt on telegram @KingVJ01

import asyncio
import datetime
import time

from pyrogram import Client, filters
from pyrogram.errors import (
    InputUserDeactivated,
    UserNotParticipant,
    FloodWait,
    UserIsBlocked,
    PeerIdInvalid
)

from plugins.dbusers import db
from config import ADMINS


async def broadcast_messages(user_id: int, message) -> tuple[bool, str]:
    """
    Broadcast a message to a single user, handling common errors.
    """
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(user_id)
        return False, "Error"
    except Exception:
        return False, "Error"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    """
    Broadcast a replied message to all users in the database.
    """
    users_cursor = db.get_all_users()
    b_msg = message.reply_to_message
    status_msg = await message.reply_text("**Broadcasting your messages...**")

    start_time = time.time()
    total_users = await db.total_users_count()
    done = success = blocked = deleted = failed = 0

    async for user in users_cursor:
        user_id = user.get("id")
        if not user_id:
            failed += 1
            done += 1
            continue

        sent, status = await broadcast_messages(user_id, b_msg)
        if sent:
            success += 1
        else:
            if status == "Blocked":
                blocked += 1
            elif status == "Deleted":
                deleted += 1
            else:
                failed += 1
        done += 1

        # Update status every 20 messages
        if done % 20 == 0 or done == total_users:
            try:
                await status_msg.edit(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"✅ Success: {success}\n"
                    f"🚫 Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n"
                    f"⚠️ Failed: {failed}"
                )
            except Exception:
                pass

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await status_msg.edit(
        f"✅ Broadcast Completed\n"
        f"Time Taken: {time_taken}\n\n"
        f"Total Users: {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"✅ Success: {success}\n"
        f"🚫 Blocked: {blocked}\n"
        f"❌ Deleted: {deleted}\n"
        f"⚠️ Failed: {failed}"
    )
