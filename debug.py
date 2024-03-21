import os
import json
from dotenv import load_dotenv

from matchwatch.main import ForwardToTelegram, GetPoint


load_dotenv()

accounts = json.loads(os.environ.get("ACCOUNTS"))
for acc in accounts:
    res = GetPoint(acc["account"], acc["password"])
    print(json.dumps(res))
    ForwardToTelegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), res)
