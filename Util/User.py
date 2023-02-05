# Static variable
import Static as static
import Util.Message as message

def is_user_allowed(db_client, user_id):
    return user_id == "aryodh" or db_client.read_user_allowed_by_user_id(user_id)

def user_not_allowed(chat_id):
    response = "You are not allowed!\nPlease contact @aryodh"
    return message.send_message(response, chat_id)

def check_user_username(username, chat_id):
    response = "@" + username
    return message.send_message(response, chat_id)

def add_user_permission(db_client, username, chat_id):
    if len(username) == 1:
        username = username[0]
        isSuccess = db_client.add_allowed_user(username)
        if isSuccess[static.IS_SUCCESS_KEY]:
            response = "Success to add user!"
        else:
            response = "Failed to add user!"
    else:
        response = "Please specify the user want to be add"

    return message.send_message(response, chat_id)
