from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

from telegram.telegram_alerts import (
    TelegramAlerts
)

bot = TelegramAlerts(
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

bot.send(
    "🚀 APEX TRADER TEST ALERT"
)