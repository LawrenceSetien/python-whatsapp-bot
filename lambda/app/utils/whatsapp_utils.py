import re
import json
import logging
import requests
from flask import current_app, jsonify
from app.services.openai_service import generate_response



def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_upper_case_response(response):
    """
    Return text in uppercase.
    """
    return response.upper()


def send_message(data):
    """
    Sends a message using the Facebook Graph API.
    Args:
        data (dict): The message payload to be sent in JSON format.

    Returns:
        Response object or tuple: The HTTP response from the Facebook Graph API if successful.
                                  If an error occurs, returns a JSON response with an error message
                                  and an appropriate HTTP status code.
    """
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    """
    Processes a given text to make it compatible with WhatsApp formatting.

    This function performs two main tasks:
    1. Removes any content enclosed in brackets "【 】".
    2. Converts text enclosed in double asterisks "** **" to single asterisks "* *",
       which is the markdown format used in WhatsApp to denote bold text.

    Args:
        text (str): The input string that needs to be processed.

    Returns:
        str: The processed text, formatted for WhatsApp.
    """
    # Remove brackets
    pattern = r"\【.*?\】"

    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    """
    Processes an incoming WhatsApp message and sends an appropriate response.

    This function extracts the WhatsApp ID, sender's name, and the message content
    from the incoming webhook `body`. It then generates a response based on the
    message content and sends this response back to the user using the WhatsApp API.

    Args:
        body (dict): The webhook payload from WhatsApp containing the message data.

    Returns:
        None
    """

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # Option 1: Return same text in upper case
    # response = generate_upper_case_response(message_body)

    # Option 2: OpenAI Integration
    response = generate_response(message_body, wa_id, name)
    response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
