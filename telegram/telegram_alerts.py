import requests


class TelegramAlerts:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send(self, message):

        if not self.token or not self.chat_id:
            print("Telegram not configured")
            return

        url = (
            f"https://api.telegram.org/bot"
            f"{self.token}/sendMessage"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        requests.post(url, json=payload, timeout=15)