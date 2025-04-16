import sys
import requests
import json
import os

# Add the parent directory to the Python path so you can import from the 'telegram' package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.main import send_telegram_message


def get_working_money_tracking_numbers():
    page_id = "143a14eca444805cbd24cbf977997031"  # Working Money Database
    token = os.environ.get("NOTION_DAILY_TASK_TOKEN")

    url = f"https://api.notion.com/v1/databases/{page_id}/query"
    headers = {
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Bilyet Shipment",
                    "rich_text": {
                        "is_not_empty": True,
                    },
                },
                {
                    "property": "Invest Status",
                    "status": {
                        "equals": "Active",
                    },
                },
            ],
        },
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        # Extract data
        extracted_data = []

        results = response.json().get("results", [])

        for result in results:
            properties = result.get("properties", {})
            bilyet_shipment_data = properties.get("Bilyet Shipment", {}).get(
                "rich_text", []
            )
            invest_value = properties.get("Invest Value", {}).get("number")
            invest_target_data = properties.get("Invest Target", {}).get("select", {})

            bilyet_shipment = (
                bilyet_shipment_data[0]["plain_text"] if bilyet_shipment_data else None
            )
            invest_target = (
                invest_target_data.get("name") if invest_target_data else None
            )

            extracted_data.append(
                {
                    "Bilyet Shipment": bilyet_shipment,
                    "Invest Value": invest_value,
                    "Invest Target": invest_target,
                }
            )

        return extracted_data

    except requests.exceptions.RequestException as e:
        error_message = f"Error querying Notion API: {e}"
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


def track_shipments(reference_numbers, logistic_id=1):
    # API endpoint
    url = "https://gql-web.shipper.id/query"

    # Headers from the curl command
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://shipper.id",
        "priority": "u=1, i",
        "referer": "https://shipper.id/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-app-name": "shp-homepage-v5",
        "x-app-version": "1.0.0",
    }

    # GraphQL query
    query = """
    query trackingDirect($input: TrackingDirectInput!) {
      trackingDirect(p: $input) {
        referenceNo
        logistic {
          id
          __typename
        }
        shipmentDate
        details {
          datetime
          shipperStatus {
            name
            description
            __typename
          }
          logisticStatus {
            name
            description
            __typename
          }
          __typename
        }
        consigner {
          name
          address
          __typename
        }
        consignee {
          name
          address
          __typename
        }
        __typename
      }
    }
    """

    # Ensure reference_numbers is a list
    if isinstance(reference_numbers, str):
        reference_numbers = [reference_numbers]

    # Variables for the query
    variables = {"input": {"logisticId": logistic_id, "referenceNo": reference_numbers}}

    # Prepare the payload
    payload = {
        "operationName": "trackingDirect",
        "query": query,
        "variables": variables,
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()

        # Parse the response data
        parsed_data = []
        tracking_data = response_data.get("data", {}).get("trackingDirect", [])

        for shipment in tracking_data:
            reference_no = shipment.get("referenceNo")
            details = shipment.get("details", [])
            shipment_details = []

            for detail in details:
                datetime = detail.get("datetime")
                logistic_status = detail.get("logisticStatus", {}).get("description")

                shipment_details.append(
                    {
                        "datetime": datetime,
                        "logistic_status": logistic_status,
                    }
                )

            parsed_data.append(
                {
                    "reference_no": reference_no,
                    "details": shipment_details,
                }
            )
        return parsed_data

    except requests.exceptions.RequestException as e:
        error_message = f"Error tracking shipments: {e}"
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


def combine_tracking_data(tracking_data):
    combined_results = []
    seen_reference_numbers = {}

    for item in tracking_data:
        reference_no = item["Bilyet Shipment"]
        invest_value = item.get("Invest Value", 0)

        if reference_no in seen_reference_numbers:
            # If the reference number already exists, sum the Invest Value
            seen_reference_numbers[reference_no]["working_money_data"][
                "Invest Value"
            ] += invest_value
        else:
            # Add a new entry for the reference number
            seen_reference_numbers[reference_no] = {
                "working_money_data": item,
                "shipment_data": {
                    "reference_no": reference_no,
                    "last_detail": None,
                },
            }

    # Convert the dictionary back to a list
    combined_results = list(seen_reference_numbers.values())
    return combined_results


def format_shipment_message(data):
    """
    Formats the shipment tracking data into a nicely formatted message.
    """

    message_lines = []
    for item in data:
        notion_data = item["working_money_data"]
        shipment_data = item["shipment_data"]
        message_lines.extend(
            [
                f"*Reference Number:* {shipment_data['reference_no']}",
                f"*Invest Value:* {notion_data['Invest Value']}",
                f"*Invest Target:* {notion_data['Invest Target']}",
            ]
        )
        if shipment_data["last_detail"]:
            message_lines.extend(
                [
                    f"*Last Update:* {shipment_data['last_detail']['datetime']}",
                    f"🚚 *Status:* {shipment_data['last_detail']['logistic_status']}\n",
                ]
            )
        else:
            message_lines.append("⚠️ *Status:* No tracking details available.\n")
    return "\n".join(message_lines)


def main():
    title = "📦 Shipment Tracking Update"
    hashtag = "shipmenttracking"
    try:
        tracking_data = get_working_money_tracking_numbers()

        # Combine the data first
        combined_results = combine_tracking_data(tracking_data)

        # Extract tracking numbers from the combined data
        tracking_numbers = [
            item["shipment_data"]["reference_no"] for item in combined_results
        ]

        # Track shipments
        shipment_results = track_shipments(tracking_numbers)

        # Update combined results with tracking details
        for i, shipment_result in enumerate(shipment_results):
            last_detail = None
            if shipment_result["details"]:
                last_detail = shipment_result["details"][-1]  # Get the last detail

            combined_results[i]["shipment_data"]["last_detail"] = last_detail

        # Format and send the message
        formatted_message = format_shipment_message(combined_results)
        send_telegram_message(title, formatted_message, hashtag)
    except Exception as e:
        send_telegram_message(title, f"An error occurred: {e}", hashtag)


if __name__ == "__main__":
    main()
