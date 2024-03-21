import os
import json
from dotenv import load_dotenv

from matchwatch.scraper import GetPoint
from matchwatch.telegram import ForwardToTelegram

load_dotenv()
accounts = json.loads(os.environ.get("ACCOUNTS"))
for acc in accounts:
    # print(acc.account)
    print(acc["account"])

# res = GetPoint(os.environ.get("ACCOUNT2"), os.environ.get("PASSWORD2"))
# print("res", json.dumps(res))
# ForwardToTelegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), res)
