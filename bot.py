import requests
import json
import time


# =========================
# CONFIGURATION
# =========================

BOT_TOKEN = "8912306029:AAELo72Pcke8bOvktPERJwl2PVqTfApuuTk"
EXTERNAL_API_URL = "https://ethicaltabbo.in/api/lookup"

TELEGRAM_API_URL = "https://api.telegram.org/bot" + BOT_TOKEN


# =========================
# TELEGRAM API FUNCTIONS
# =========================

def get_updates(offset=None):
    url = TELEGRAM_API_URL + "/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()

    except Exception as error:
        print("getUpdates error:", error)
        return {}


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = TELEGRAM_API_URL + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(url, data=data, timeout=15)
        return response.json()

    except Exception as error:
        print("sendMessage error:", error)
        return {}


# =========================
# KEYBOARD
# =========================

def main_keyboard():
    return {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# =========================
# HTML ESCAPE FUNCTION
# =========================

def escape_html(text):
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


# =========================
# PHONE LOOKUP
# =========================

def phone_lookup(phone_number):
    if EXTERNAL_API_URL == "":
        return {
            "error": "External API URL is not configured."
        }

    try:
        # Example:
        # https://example.com/api?phone=1234567890
        #
        # Change the parameter below if your educational/test API
        # expects a different parameter name.

        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=20
        )

        # Convert API response to JSON
        api_data = response.json()

        return api_data

    except ValueError:
        return {
            "error": "The external API did not return valid JSON."
        }

    except requests.exceptions.RequestException as error:
        return {
            "error": "External API request failed.",
            "details": str(error)
        }

    except Exception as error:
        return {
            "error": "Unexpected error.",
            "details": str(error)
        }


# =========================
# MESSAGE HANDLER
# =========================

def handle_message(message):
    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # -------------------------
    # /start COMMAND
    # -------------------------

    if text == "/start":
        welcome_message = (
            "👋 Welcome!\n\n"
            "Use the button below to continue."
        )

        send_message(
            chat_id,
            welcome_message,
            reply_markup=main_keyboard()
        )

        return

    # -------------------------
    # PHONE LOOKUP BUTTON
    # -------------------------

    if text == "📱 Phone Lookup":
        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:",
            reply_markup=main_keyboard()
        )

        return

    # -------------------------
    # PHONE NUMBER VALIDATION
    # -------------------------

    if text.isdigit() and len(text) == 10:

        send_message(
            chat_id,
            "🔎 Looking up the number..."
        )

        result = phone_lookup(text)

        # Convert JSON object to readable JSON text
        formatted_json = json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )

        # Escape HTML so API data cannot break <pre>
        formatted_json = escape_html(formatted_json)

        output = "<pre>" + formatted_json + "</pre>"

        send_message(
            chat_id,
            output,
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )

        return

    # -------------------------
    # INVALID INPUT
    # -------------------------

    error_message = (
        "❌ Invalid input.\n\n"
        "Please send exactly 10 digits.\n"
        "Example: 3001234567"
    )

    send_message(
        chat_id,
        error_message,
        reply_markup=main_keyboard()
    )


# =========================
# MAIN LONG-POLLING LOOP
# =========================

def main():
    if BOT_TOKEN == "":
        print("ERROR: BOT_TOKEN is empty.")
        print("Add your Telegram bot token to BOT_TOKEN.")
        return

    print("Bot started...")
    print("Waiting for messages...")

    offset = None

    while True:
        try:
            updates = get_updates(offset)

            if not updates:
                time.sleep(2)
                continue

            if not updates.get("ok"):
                print("Telegram API error:", updates)
                time.sleep(3)
                continue

            for update in updates.get("result", []):

                # Move offset forward so the same update
                # is not processed again.
                offset = update["update_id"] + 1

                if "message" in update:
                    handle_message(update["message"])

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break

        except Exception as error:
            print("Main loop error:", error)
            time.sleep(3)


# =========================
# START BOT
# =========================

if __name__ == "__main__":
    main()
