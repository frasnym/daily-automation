from datetime import datetime, timezone
import json
import os
import sys
import requests
import pytz

# Add the parent directory to the Python path so you can import from the 'telegram' package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.main import send_telegram_message


def fetch_match_results():
    """Fetch match results from the API."""

    try:
        url = "https://cdnapi.manutd.com/api/v1/en/id/all/web/list/matchresult/sid:2024~isMU:true/0/30"
        headers = {
            "x-api-key": os.environ.get("MANUTD_APIKEY"),
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"Error request: {e}"
        if "response" in locals() and response is not None:
            error_message += f"\nResponse status code: {response.status_code}"
            try:
                error_message += f"\nResponse body: {response.json()}"
            except json.JSONDecodeError:
                error_message += f"\nResponse body (non-JSON): {response.text}"
        raise Exception(error_message)

    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON response: {e}"
        if "response" in locals() and response is not None:
            error_message += f"\nResponse status code: {response.status_code}"
            error_message += f"\nResponse body: {response.text}"
        raise Exception(error_message)
    except (AttributeError, KeyError, TypeError) as e:
        raise Exception(f"Error parsing shipment tracking data: {e}")


def process_match_data(data) -> str:
    """Process the match data and return the results formatted as text."""

    try:
        now = datetime.now(timezone.utc)
        result = ""

        result_docs = (
            data.get("ResultListResponse", {}).get("response", {}).get("docs", [])
        )

        for doc in result_docs:
            match_date_str = doc["matchdate_tdt"]
            match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
            time_difference = (now - match_date).days

            # Skip matches older than 2 days
            if time_difference > 2:
                break

            is_mu_home = doc["hometeamid_t"] == "1"

            home_score = doc["resultdata_t"]["HomeResult"]["Score"]
            away_score = doc["resultdata_t"]["AwayResult"]["Score"]
            competition = doc["competitionname_t"]

            # Format date
            tz_jakarta = pytz.timezone("Asia/Jakarta")
            date_obj_jakarta = match_date.astimezone(tz_jakarta)
            match_date_str = str(date_obj_jakarta)

            # Determine match result (WIN, LOSE, or DRAW)
            result_txt = "ERROR"
            if home_score > away_score:
                result_txt = "WIN" if is_mu_home else "LOSE"
            elif home_score < away_score:
                result_txt = "WIN" if not is_mu_home else "LOSE"
            else:
                result_txt = "DRAW"

            # Format the match result text
            result += (
                f"{result_txt} in {competition} on {match_date_str}\n"
                f"{doc['hometeam_t']} ({home_score}) - ({away_score}) {doc['awayteam_t']}\n\n"
            )

        return result
    except Exception as e:
        raise Exception(f"Error processing match data: {e}")


def format_message(result: str) -> str:
    """Format the result and forward it to Telegram."""
    messages: list[str] = []

    if result == "":
        messages.append("No match results found.")
    else:
        messages.append(result)

    final_message = "\n".join(messages)

    return final_message


def main():
    """Run the script and send the result to Telegram."""

    title = "⚽ Manchester United Daily Match Result"
    hashtag = "manutd"

    try:
        # Fetch data from the API
        match_result = fetch_match_results()
        print("fetch api success")

        resProcess = process_match_data(match_result)
        print("process api success")

        send_telegram_message(title, format_message(resProcess), hashtag)
    except Exception as e:
        send_telegram_message(title, f"An error occurred: {e}", hashtag)


# Call the main function if this script is executed
if __name__ == "__main__":
    main()
