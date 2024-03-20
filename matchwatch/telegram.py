import requests


# Send the message using the Telegram bot API
def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message. Status code: {response.status_code}")


def ForwardToTelegram(BOT_TOKEN: str, CHAT_ID: str, result: dict):
    messages: list[str] = []
    messages.append("from: py-matchwatch-loggin #matchwatch\n")
    messages.append("username: {}".format(result["username"]))
    if result["err"] is not None:
        messages.append("err: {}".format(result["err"]))
        messages.append("process: {}".format(result["process"]))
    else:
        messages.append("point: {}".format(result["point"]))
        messages.append("last: {}".format(result["last"]))

    separator = "\n"  # Customize the separator as needed
    finalMessage = separator.join(str(x) for x in messages)

    send_telegram_message(BOT_TOKEN, CHAT_ID, finalMessage)
