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
API_ID = int(os.environ.get("API_ID", "2468192:))
API_HASH = os.environ.get("API_HASH", "4906b3f8f198ec0e24edb2c197677678")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "File_StoreRobot")  # without @
PORT = int(os.environ.get("PORT", 8080))

PICS = os.environ.get('PICS', 'https://telegra.ph/file/4466d37d43f5703516f74.jpg').split()
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMINS', '2098589219').split()]

# -------------------------------
# Clone Mode
# -------------------------------
CLONE_MODE = is_enabled(os.environ.get('CLONE_MODE', "False"))
CLONE_DB_URI = os.environ.get("CLONE_DB_URI", "")
CDB_NAME = os.environ.get("CDB_NAME", "clonetechvj")

# -------------------------------
# Database Information
# -------------------------------
DB_URI = os.environ.get("DB_URI", "mongodb+srv://Filter01:ei62heT4O81OyNyl@Filter01.6kyybcz.mongodb.net/?retryWrites=true&w=majority&appName=Filter01")
DB_NAME = os.environ.get("DB_NAME", "Filter1")

# -------------------------------
# Auto Delete Information
# -------------------------------
AUTO_DELETE_MODE = is_enabled(os.environ.get('AUTO_DELETE_MODE', "True"))
AUTO_DELETE = int(os.environ.get("AUTO_DELETE", 30))  # in minutes
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 1800))  # in seconds

# -------------------------------
# Channel / Logging Information
# -------------------------------
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001683081282"))

# -------------------------------
# File Caption Information
# -------------------------------
CUSTOM_FILE_CAPTION = os.environ.get("CUSTOM_FILE_CAPTION", "Uploaded by @KR_Picture")
BATCH_FILE_CAPTION = os.environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
PUBLIC_FILE_STORE = is_enabled(os.environ.get('PUBLIC_FILE_STORE', "False"))

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
WEBSITE_URL_MODE = is_enabled(os.environ.get('WEBSITE_URL_MODE', "True"))
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://krpicture0.blogspot.com/2025/08/krpicture.html")

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
