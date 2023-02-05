import json

# Static variable
import Static as static

def check_event_type(event):
    try:
        json.loads(event["body"])
        return static.EVENT_HTTP_TYPE
    except Exception:
        if list(event.values())[0]['event'] == "scheduler":
            return static.EVENT_SCHEDULER_TYPE
    return static.EVENT_UNKNOWN_TYPE

def check_message_type(data):
    if "message" in data and "chat" in data["message"] and "id" in data["message"]["chat"]:
        return static.MESSAGE_CHAT_TYPE
    
    return static.MESSAGE_UNKNOWN_TYPE