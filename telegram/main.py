import os
import requests


def send_telegram_message(title: str, body: str, hashtag: str):
    """
    Send a message via Telegram bot API.
    """

    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        print("Bot token or chat ID not set.")
        return

    text = ""
    text += f"*{title}*\n\n"
    text += f"*{body}*"

    footer = f"source: `{os.environ.get('APP')}`"
    text += f"\n\n{footer}"

    tags = ["dailyautomation", hashtag]
    tagsStr = " ".join(f"#{item}" for item in tags)
    text += f"\n{tagsStr}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params: dict[str, str] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }  # Added parse_mode
    response = requests.post(url, json=params)  # changed to post, and json=params
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(response.text)
        print(f"Error sending message. Status code: {response.status_code}")
