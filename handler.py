import json
import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import requests

# Internal Library
import Accessor.Dynamodb as dynamodb
import Recurring.Recurring as recurring
import Recurring.Subscriber as subscriber
import Util.Event as eventUtil
import Util.Message as message
import Util.Stock as stockUtil
import Util.User as user

# Static variable
import Static as static

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_client = dynamodb.Dynamodb()

def hello(event, context):
    url = static.BASE_URL + "/sendMessage"

    event_type = eventUtil.check_event_type(event)
    if event_type == static.EVENT_SCHEDULER_TYPE:
        return recurring.lunch_update(db_client)

    data = json.loads(event["body"])      
    logger.info(data)

    message_type = eventUtil.check_message_type(data)
    if message_type != static.MESSAGE_CHAT_TYPE:
        return {"statusCode": 200} # Ignoring edit message event
    
    try:
        username = data["message"]["from"]["username"]
        chat_id = data["message"]["chat"]['id']
        messages = str(data["message"]["text"]).split(" ")
        
        command = messages[0].split("@")[0] # For handling command: /watchlist@stokyo_bot

        # Check Username feature
        if command == "/checkmyusername":
            return user.check_user_username(username, chat_id)
        
        # User Permission feature
        if not user.is_user_allowed(db_client, username):
            return user.user_not_allowed(chat_id)

        if command == "/adduserpermission":
            return user.add_user_permission(db_client, messages[1:], chat_id)

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
            if len(messages) > 2:
                stocks = messages[1:]
                stocks = [x.upper() for x in stocks]
                user_stock_list = db_client.read_user_stock_list(username)
                if user_stock_list is None or len(user_stock_list) == 0:
                    isSuccess = db_client.create_user_stock(username, chat_id, stocks)
                else:
                    user_stock_list += stocks
                    isSuccess = db_client.update_user_stocks(username, user_stock_list)
                response = (', '.join(stocks) + " is success to add!\nSee your watchlist: /watchlist")
            elif len(messages) > 1:
                stock = messages[1].upper()
                user_stock_list = db_client.read_user_stock_list(username)
                if user_stock_list is None or len(user_stock_list) == 0:
                    stocks = [messages[1].upper()]
                    isSuccess = db_client.create_user_stock(username, chat_id, stocks)
                else:
                    isSuccess = db_client.add_user_stock(username, user_stock_list, stock)
                response = (stock + " is success to add!\nSee your watch list: /watchlist") if isSuccess else "Error adding stock.\nPlease try again."
            else:
                response = "Please define the stock you want to add"
        elif command == "/removestock":
            if len(messages) > 1:
                stock = messages[1].upper()
                user_stock_list = db_client.read_user_stock_list(username)
                if len(user_stock_list) > 0:
                    isSuccess = db_client.remove_user_stock(username, user_stock_list, stock)
                    response = (stock + " is success to remove!\nSee your watch list: /watchlist" if isSuccess else "Error removing stock.\nPlease try again.")
                else:
                    response = "Watch list already empty!"
        elif command == "/watchlist":
            stocks =  db_client.read_user_stock_list(username)
            if stocks is None or len(stocks) == 0:
                response = "Your watch list is empty!"
            else:
                response = "Your watch list:"
                for stock in stocks:
                    response += "\n• " + stock 
        
        # Stock feature
        elif command == "/checkstock":
            if messages[1:]:
                stock = messages[1].upper()
                return stockUtil.check_stock(stock, "", chat_id)

        elif command == "/checkstockidx":
            if messages[1:]:
                stock = messages[1].upper()
                return stockUtil.check_stock(stock, ticker, chat_id)
    
        elif command == "/stockrecom":
            if messages[1:]:
                stock = messages[1].upper()
                return stockUtil.check_stock_recommendation(stock, "", chat_id)

        elif command == "/stockrecomidx":
            if messages[1:]:
                stock = messages[1].upper()
                ticker = "JK"
                return stockUtil.check_stock_recommendation(stock, ticker, chat_id)
        else:
            response = "Command not found!"

    except Exception as e:
        logger.error(e)
        response = "Exception: " + str(e)

    if response:
        return message.send_message(response, chat_id)
    else:
        return {"statusCode": 200}


