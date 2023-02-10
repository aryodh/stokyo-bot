import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import requests

# Static variable
import Static as static

def send_message(message, chat_id):
    send_message_without_return(message, chat_id)
    return {"statusCode": 200}

def send_specific_message(messages):
    user_id_target = messages[0]
    message = " ".join(messages[1:])
    return send_message(message, user_id_target)

def send_message_without_return(message, chat_id):
    data = {
        "text": message.encode("utf8"), 
        "chat_id": chat_id,
        "parse_mode": "Markdown"
    }
    requests.post(static.SEND_MESSAGE_URL, data)
