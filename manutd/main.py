from datetime import datetime, timezone
import json
import os
import requests


def fetch_match_results(url, headers):
    """Fetch match results from the API."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"err": f"Request failed: {str(e)}"}


def process_match_data(data):
    """Process the match data and return the results formatted as text."""
    now = datetime.now(timezone.utc)
    result = {
        "result": "",
        "process": [],
        "err": None,
    }

    result_docs = data.get("ResultListResponse", {}).get("response", {}).get("docs", [])
    for doc in result_docs:
        match_date_str = doc["matchdate_tdt"]
        match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
        time_difference = (now - match_date).days

        # Skip matches older than 2 days
        if time_difference > 2:
            break

        home_score = doc["resultdata_t"]["HomeResult"]["Score"]
        away_score = doc["resultdata_t"]["AwayResult"]["Score"]
        competition = doc["competitionname_t"]
        match_date_str = match_date.strftime("%Y-%m-%d")

        # Determine match result (WIN, LOSE, or DRAW)
        result_txt = "DRAW"  # Default result if no MatchWinner
        if "MatchWinner" in doc["resultdata_t"]:
            match_winner = doc["resultdata_t"]["MatchWinner"]
            result_txt = "WIN" if match_winner == "1" else "LOSE"

        # Format the match result text
        result["result"] += (
            f"{result_txt} in {competition} on {match_date_str}\n"
            f"{doc['hometeam_t']} ({home_score}) - ({away_score}) {doc['awayteam_t']}\n\n"
        )

    return result


def send_telegram_message(token, chat_id, text):
    """Send the formatted message to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message. Status code: {response.status_code}")


def forward_to_telegram(bot_token, chat_id, result):
    """Format the result and forward it to Telegram."""
    messages = [f"source: {os.environ.get('APP')} #manutd\n"]

    if not result.get("result"):
        messages.append("No match results found.")
    else:
        messages.append(result["result"])

    if result.get("err"):
        messages.append(f"Error: {result['err']}")

    final_message = "\n".join(messages)
    send_telegram_message(bot_token, chat_id, final_message)


def run():
    """Main function to fetch and process match results."""
    result = {
        "result": "",
        "process": [],
        "err": None,
    }

    url = "https://cdnapi.manutd.com/api/v1/en/id/all/web/list/matchresult/sid:2024~isMU:true/0/30"
    headers = {
        "x-api-key": os.environ.get("MANUTD_APIKEY"),
    }

    # Fetch data from the API
    data = fetch_match_results(url, headers)

    if "err" in data:
        result["err"] = data["err"]
        return result

    result["process"].append("success GET api")

    resProcess = process_match_data(data)

    result["result"] = resProcess["result"]
    result["process"].extend(resProcess["process"])
    if resProcess["err"]:
        result["err"] = resProcess["err"]

    return result


def main():
    """Run the script and send the result to Telegram."""
    res = run()
    print(json.dumps(res))
    forward_to_telegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), res)


# Call the main function if this script is executed
if __name__ == "__main__":
    main()
