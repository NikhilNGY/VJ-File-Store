# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from TechVJ.Script import script 
from datetime import datetime
from typing import Optional


class Script:
    START_TXT = (
        "<b>ʜᴇʟʟᴏ {user_name}, ᴍʏ ɴᴀᴍᴇ {bot_name} 👋, "
        "ɪ ᴀᴍ ʟᴀᴛᴇꜱᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴅ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ + "
        "sᴛʀᴇᴀᴍ / ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ꜰᴇᴀᴛᴜʀᴇ + "
        "ᴄᴜꜱᴛᴏᴍ ᴜʀʟ ꜱʜᴏʀᴛɴᴇʀ ꜱᴜᴘᴘᴏʀᴛ + ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ sᴜᴘᴘᴏʀᴛ "
        "ᴀɴᴅ ʙᴇꜱᴛ ᴜɪ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ </b>"
    )

    CAPTION = (
        "<b>📂 ғɪʟᴇɴᴀᴍᴇ : {file_name}\n"
        "⚙️ sɪᴢᴇ : {file_size}\n"
        "Jᴏɪɴ [ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ](https://t.me/vj_botz)</b>"
    )

    SHORTENER_API_MESSAGE = (
        "<b>Tᴏ ᴀᴅᴅ ᴏʀ ᴜᴘᴅᴀᴛᴇ ʏᴏᴜʀ Sʜᴏʀᴛɴᴇʀ Wᴇʙsɪᴛᴇ API, /api (ᴀᴘɪ)\n"
        "Ex: /api {example_api}\n\n"
        "<b>Cᴜʀʀᴇɴᴛ Wᴇʙsɪᴛᴇ: {base_site}\n"
        "Cᴜʀʀᴇɴᴛ Sʜᴏʀᴛᴇɴᴇʀ API:</b> `{shortener_api}`\n\n"
        "To remove, send: `/api None`</b>"
    )

    ABOUT_TXT = (
        "<b>🤖 ᴍʏ ɴᴀᴍᴇ: {bot_name}\n"
        "📝 ʟᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>Python 3</a>\n"
        "📚 ʟɪʙʀᴀʀʏ: <a href=https://docs.pyrogram.org>Pyrogram</a>\n"
        "🧑🏻‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href=https://t.me/Kingvj01>Tech VJ</a>\n"
        "👥 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ: <a href=https://t.me/VJ_Bot_Disscussion>VJ Support</a>\n"
        "📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ: <a href=https://t.me/vj_botz>VJ Update</a></b>"
    )

    HELP_TXT = (
        "<b><u>💢 HOW TO USE THE BOT ☺️</u>\n\n"
        "🔻 /link - Reply to a video or file to get shareable link\n"
        "🔻 /batch - Send first link of file store channel post then last post link\n"
        "🔻 /base_site - Set your URL shortener link domain\n"
        "🔻 /api - Set URL shortener API\n"
        "🔻 /broadcast - Broadcast a message (bot owner only)</b>"
    )

    LOG_TEXT = "<b>#NewUser\n\nID - <code>{user_id}</code>\nName - {user_name}</b>"

    RESTART_TXT = (
        "<b>Bot Restarted!\n\n"
        "📅 Date: <code>{date}</code>\n"
        "⏰ Time: <code>{time}</code>\n"
        "🌐 Timezone: <code>Asia/Kolkata</code>\n"
        "🛠️ Build Status: <code>v2.7.1 [Stable]</code></b>"
    )

    @classmethod
    def format_start(cls, user_name: str, bot_name: str) -> str:
        return cls.START_TXT.format(user_name=user_name, bot_name=bot_name)

    @classmethod
    def format_caption(cls, file_name: str, file_size: str) -> str:
        return cls.CAPTION.format(file_name=file_name, file_size=file_size)

    @classmethod
    def format_shortener_api_message(cls, base_site: str, shortener_api: str, example_api: str) -> str:
        return cls.SHORTENER_API_MESSAGE.format(
            base_site=base_site, shortener_api=shortener_api, example_api=example_api
        )

    @classmethod
    def format_log(cls, user_id: int, user_name: str) -> str:
        return cls.LOG_TEXT.format(user_id=user_id, user_name=user_name)

    @classmethod
    def format_restart(cls, dt: Optional[datetime] = None) -> str:
        dt = dt or datetime.now()
        return cls.RESTART_TXT.format(date=dt.date(), time=dt.strftime("%H:%M:%S %p"))

# This defines the script function
def script():
    return "Script is running"

