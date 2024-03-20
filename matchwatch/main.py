import os
from matchwatch.scraper import GetPoint
from matchwatch.telegram import ForwardToTelegram


def main():
    acc1 = GetPoint(os.environ.get("ACCOUNT1"), os.environ.get("PASSWORD1"))
    ForwardToTelegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), acc1)

    acc2 = GetPoint(os.environ.get("ACCOUNT2"), os.environ.get("PASSWORD2"))
    ForwardToTelegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), acc2)


# Call the main function if this script is executed
if __name__ == "__main__":
    main()
