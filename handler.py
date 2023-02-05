import json
import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import requests

# Internal Library
import Accessor.Dynamodb as dynamodb
import Feature.Recurring.Recurring as recurring
import Feature.Recurring.Subscriber as subscriber
import Feature.Watchlist.Watchlist as watchlist
import Util.Event as event_util
import Util.Message as message
import Util.Stock as stock_util
import Util.User as user_util

# Static variable
import Static as static

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_client = dynamodb.Dynamodb()

def hello(event, context):

    event_type = event_util.check_event_type(event)
    if event_type == static.EVENT_SCHEDULER_TYPE:
        return recurring.lunch_update(db_client)

    data = json.loads(event["body"])      
    logger.info(data)

    message_type = event_util.check_message_type(data)
    if message_type != static.MESSAGE_CHAT_TYPE:
        return {"statusCode": 200} # Ignoring edit message event
    
    try:
        username = data["message"]["from"]["username"]
        chat_id = data["message"]["chat"]['id']
        messages = str(data["message"]["text"]).split(" ")
        
        command = messages[0].split("@")[0] # For handling command: /watchlist@stokyo_bot

        # Check Username feature
        if command == "/checkmyusername":
            return user_util.check_user_username(username, chat_id)
        
        # User Permission feature
        if not user_util.is_user_allowed(db_client, username):
            return user_util.user_not_allowed(chat_id)

        if command == "/adduserpermission":
            return user_util.add_user_permission(db_client, messages[1:], chat_id)

        # Recurring - Lunch Update feature
        if command == "/updatesubscribe":
            return subscriber.update_user_subscribe(db_client, username, messages[1:], chat_id)
        elif command == "/getsubscriber":
            return recurring.lunch_update(db_client)

        # Send Message to chat_id feature
        if command == "/sendMessage":
            return message.send_specific_message(messages[1:])

        # Watchlist feture | To Do: Refactor       
        if command == "/addstock":
            return watchlist.add_user_stock(db_client, username, messages[1:], chat_id)
        elif command == "/removestock":
            return watchlist.remove_user_stock(db_client, username, messages[1:], chat_id)
        elif command == "/watchlist":
            return watchlist.view_watchlist(db_client, username, chat_id)
        
        # Stock feature
        elif command == "/checkstock":
            if messages[1:]:
                stock = messages[1].upper()
                return stock_util.check_stock(stock, "", chat_id)

        elif command == "/checkstockidx":
            if messages[1:]:
                stock = messages[1].upper()
                return stock_util.check_stock(stock, ticker, chat_id)
    
        elif command == "/stockrecom":
            if messages[1:]:
                stock = messages[1].upper()
                return stock_util.check_stock_recommendation(stock, "", chat_id)

        elif command == "/stockrecomidx":
            if messages[1:]:
                stock = messages[1].upper()
                ticker = "JK"
                return stock_util.check_stock_recommendation(stock, ticker, chat_id)
        else:
            response = "Command not found!"

    except Exception as e:
        logger.error(e)
        response = "Exception: " + str(e)

    if response:
        return message.send_message(response, chat_id)
    else:
        return {"statusCode": 200}


