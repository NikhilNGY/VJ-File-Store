# -------------------------------
# Credit Tg - @VJ_Botz
# YouTube: https://youtube.com/@Tech_VJ
# Telegram Support: @KingVJ01
# -------------------------------

import os
import re

# -------------------------------
# Helper Functions
# -------------------------------
def is_enabled(value: str, default: bool = True) -> bool:
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# -------------------------------
# Regex Patterns
# -------------------------------
id_pattern = re.compile(r'^\d+$')

# -------------------------------
# Bot Information
# -------------------------------
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")  # without @
PORT = int(os.environ.get("PORT", 8080))

PICS = os.environ.get('PICS', 'https://graph.org/file/ce1723991756e48c35aa1.jpg').split()
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMINS', '').split()]

# -------------------------------
# Clone Mode
# -------------------------------
CLONE_MODE = is_enabled(os.environ.get('CLONE_MODE', "False"))
CLONE_DB_URI = os.environ.get("CLONE_DB_URI", "")
CDB_NAME = os.environ.get("CDB_NAME", "clonetechvj")

# -------------------------------
# Database Information
# -------------------------------
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "techvjbotz")

# -------------------------------
# Auto Delete Information
# -------------------------------
AUTO_DELETE_MODE = is_enabled(os.environ.get('AUTO_DELETE_MODE', "True"))
AUTO_DELETE = int(os.environ.get("AUTO_DELETE", 30))  # in minutes
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 1800))  # in seconds

# -------------------------------
# Channel / Logging Information
# -------------------------------
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))

# -------------------------------
# File Caption Information
# -------------------------------
CUSTOM_FILE_CAPTION = os.environ.get("CUSTOM_FILE_CAPTION", "Uploaded by @Tech_VJ")
BATCH_FILE_CAPTION = os.environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
PUBLIC_FILE_STORE = is_enabled(os.environ.get('PUBLIC_FILE_STORE', "True"))

# -------------------------------
# Verification Settings
# -------------------------------
VERIFY_MODE = is_enabled(os.environ.get('VERIFY_MODE', "False"))
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "")
VERIFY_TUTORIAL = os.environ.get("VERIFY_TUTORIAL", "")

# -------------------------------
# Website Info
# -------------------------------
WEBSITE_URL_MODE = is_enabled(os.environ.get('WEBSITE_URL_MODE', "False"))
WEBSITE_URL = os.environ.get("WEBSITE_URL", "")

# -------------------------------
# Stream / Multi-Client Settings
# -------------------------------
STREAM_MODE = is_enabled(os.environ.get('STREAM_MODE', "True"))
MULTI_CLIENT = is_enabled(os.environ.get('MULTI_CLIENT', "False"))
SLEEP_THRESHOLD = int(os.environ.get('SLEEP_THRESHOLD', 60))
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", 1200))  # in seconds

# -------------------------------
# Heroku / Deployment
# -------------------------------
ON_HEROKU = 'DYNO' in os.environ
URL = os.environ.get("URL", "https://your-app.herokuapp.com/")
