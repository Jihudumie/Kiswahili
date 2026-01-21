import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("URL")
PORT = int(os.getenv("PORT", 10000))

# Logging
LOG_CHAT_ID = -1002158955567

# Translation
TRANSLATION_SOURCE = "auto"
TRANSLATION_TARGET = "sw"

# Media Group Settings
MEDIA_GROUP_DEBOUNCE_SECONDS = 1
