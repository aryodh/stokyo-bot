import Util.Message as message

def update_user_subscribe(db_client, username, messages, chat_id):
    if messages:
        status = messages[0]
        if status == "on":
            db_client.update_user_subscribe(username, chat_id, True)
            status = "*ON*"
        elif status == "off":
            db_client.update_user_subscribe(username, chat_id, False)
            status = "*OFF*"
        else:
            status = "FAILED"
    else:
        status = "FAILED"
            
    response = "Subscribe to lunch update: " + status
    return message.send_message(response, chat_id)
