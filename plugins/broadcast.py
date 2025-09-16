from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from plugins.dbusers import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time

# ------------------ BROADCAST FUNCTION ------------------ #

async def broadcast_messages(user_id, message):
    """Send message to a single user with error handling"""
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception:
        return False, "Error"

# ------------------ BROADCAST COMMAND ------------------ #
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    """Broadcast reply message to all users in database"""
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("**Broadcasting your messages...**")
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    async for user in users:
        user_id = user.get('id')
        if user_id:
            sent, status = await broadcast_messages(int(user_id), b_msg)
            if sent:
                success += 1
            else:
                if status == "Blocked":
                    blocked += 1
                elif status == "Deleted":
                    deleted += 1
                else:
                    failed += 1
        else:
            failed += 1
        
        done += 1

        # Update progress every 20 users
        if done % 20 == 0 or done == total_users:
            try:
                await sts.edit(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}\n"
                    f"Failed: {failed}"
                )
            except Exception:
                pass

    time_taken = str(datetime.timedelta(seconds=int(time.time() - start_time)))
    await sts.edit(
        f"✅ Broadcast Completed!\n"
        f"Time Taken: {time_taken}\n\n"
        f"Total Users: {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}\n"
        f"Failed: {failed}"
    )

# ------------------ END ------------------ #