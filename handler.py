import json
import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import boto3
import requests
import yfinance as yf

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

USER_ID_KEY = 'userId'
CHAT_ID_KEY = 'chatId'
STOCKS_KEY = 'stocks'
ITEM_KEY = 'Item'

IS_SUCCESS_KEY = "is_success"
MESSAGE_KEY = "message"

DB_STOCKS_TABLE_NAME = 'user_stocks'
DB_USERS_TABLE_NAME = 'allowed_users'

class Dynamo:
    def __init__(self):
        dyn_accessor = boto3.resource('dynamodb')
        self.table = dyn_accessor.Table(DB_STOCKS_TABLE_NAME)
        self.user_table = dyn_accessor.Table(DB_USERS_TABLE_NAME)

    def read_user_allowed_by_user_id(self, user_id):
        try:
            data = self.user_table.get_item(
                Key = {
                    USER_ID_KEY: user_id
                }
            )
            return 'Item' in data

        except Exception as err:
            logger.error("Unexpected error: %s", err)
            raise ValueError('Exception on get_item function')

    def add_allowed_user(self, user_id):
        try:
            response = self.user_table.put_item(
                TableName = DB_USERS_TABLE_NAME,
                Item = {
                    USER_ID_KEY: user_id
                }
            )
        except Exception as err:
            logger.error("Unexpected error: %s", err)
        else:
            is_success = response['ResponseMetadata']['HTTPStatusCode'] == 200
            return self.response_generator(is_success, "")

    def read_user_stock_list(self, user_id):
        try:
            data = self.table.get_item(
                Key = {
                    USER_ID_KEY: user_id
                }
            )
            return (data.get(ITEM_KEY).get(STOCKS_KEY) if ('Item' in data) else [])

        except Exception as err:
            logger.error("Unexpected error: %s", err)
            raise ValueError('Exception on get_item function')

    def create_user_stock(self, user_id, chat_id, stock):
        try:
            stocks = [stock]
            response = self.table.put_item(
                TableName = DB_STOCKS_TABLE_NAME,
                Item = {
                    USER_ID_KEY: user_id,
                    CHAT_ID_KEY: chat_id,
                    STOCKS_KEY: stocks
                }
            )
        except Exception as err:
            logger.error("Unexpected error: %s", err)
        else:
            is_success = response['ResponseMetadata']['HTTPStatusCode'] == 200
            return self.response_generator(is_success, "Failed to add stock.")

    def update_user_stocks(self, userId, stockList):
        try:
            is_success = self.table.update_item(
                Key = {
                    USER_ID_KEY: userId
                },
                ExpressionAttributeNames={"#s": STOCKS_KEY},
                UpdateExpression="set #s = :sl",
                ExpressionAttributeValues={
                    ':sl': stockList
                },
                ReturnValues="UPDATED_NEW"
            )
            logger.info("Success write to dynamo!")
            return self.response_generator(is_success)
            
        except Exception as err:
            logger.error("Unexpected error: %s", err)
            return self.response_generator(False, "Failed to update user stock.")

    def add_user_stock(self, user_id, stock_list, stock):
        stock_list.append(stock)
        response = self.update_user_stocks(user_id, stock_list)
        return self.response_generator(response[IS_SUCCESS_KEY], "Succeed to add on your list: " + stock)

    def remove_user_stock(self, user_id, stock_list, stock):
        if stock in stock_list:
            stock_list.remove(stock)
            response = self.update_user_stocks(user_id, stock_list)
            if response[IS_SUCCESS_KEY]:
                return self.response_generator(True, "Succeed to remove from your list: " + stock)
            else:
                return response
        else:
            return self.response_generator(False, stock + " is not found on your list")

    def response_generator(self, is_success, message=""):
        return {
            IS_SUCCESS_KEY: is_success,
            MESSAGE_KEY: message
        }


db_client = Dynamo()

def hello(event, context):
    url = BASE_URL + "/sendMessage"
    
    data = json.loads(event["body"])
    logger.info(data)
    try:
        chat_id = data["message"]["chat"]["id"]
    except:
        return {"statusCode": 200}
    try:
        username = data["message"]["from"]["username"]

        chat_id = data["message"]["chat"]['id']
        message = str(data["message"]["text"]).split(" ")
        
        command = message[0].split("@")[0]
        logger.info("Received command: %s", command)
        
        if command == "/checkmyusername":
            response = "@" + username
            data = {"text": response.encode("utf8"), "chat_id": chat_id}
        
            requests.post(url, data)
            return {"statusCode": 200}

        if not is_user_allowed(username):
            response = "You are not allowed!\nPlease contact @aryodh"
            data = {"text": response.encode("utf8"), "chat_id": chat_id}
        
            requests.post(url, data)
            return {"statusCode": 200}

        if command == "/adduserpermission":
            if len(message) > 1:
                username = message[1]
                isSuccess = db_client.add_allowed_user(username)
                if isSuccess[IS_SUCCESS_KEY]:
                    response = "Success to add user!"
                else:
                    response = "Failed to add user!"
            else:
                response = "Please specify the user want to be add"

            data = {"text": response.encode("utf8"), "chat_id": chat_id}
    
            requests.post(url, data)
            return {"statusCode": 200}

        if command == "/addstock":
            if len(message) > 1:
                stock = message[1].upper()
                user_stock_list = db_client.read_user_stock_list(username)
                if len(user_stock_list) == 0:
                    isSuccess = db_client.create_user_stock(username, chat_id, stock)
                else:
                    isSuccess = db_client.add_user_stock(username, user_stock_list, stock)
                response = (stock + " is success to add!\nSee your watch list: /watchlist") if isSuccess else "Error adding stock.\nPlease try again."
            else:
                response = "Please define the stock you want to add"
        elif command == "/removestock":
            if len(message) > 1:
                stock = message[1].upper()
                user_stock_list = db_client.read_user_stock_list(username)
                if len(user_stock_list) > 0:
                    isSuccess = db_client.remove_user_stock(username, user_stock_list, stock)
                    response = (stock + " is success to remove!\nSee your watch list: /watchlist" if isSuccess else "Error removing stock.\nPlease try again.")
                else:
                    response = "Watch list already empty!"

        
        elif command == "/watchlist":
            stocks =  db_client.read_user_stock_list(username)
            if len(stocks) == 0:
                response = "Your watch list is empty!"
            else:
                response = "Your watch list:"
                for stock in stocks:
                    response += "\n- " + stock 
        elif command == "/checkstock":
            if len(message) > 1:
                stock = message[1].upper()
                stock_response = check_stock(stock, "")
                response = stock_response
        elif command == "/checkstockidx":
            if len(message) > 1:
                stock = message[1].upper()
                stock_response = check_stock(stock, "JK")
                response = stock_response
        elif command == "/stockrecom":
            if len(message) > 1:
                stock = message[1].upper()
                stock_response = check_stock_recommendation(stock, "")
                response = stock_response
        elif command == "/stockrecomidx":
            if len(message) > 1:
                stock = message[1].upper()
                stock_response = check_stock_recommendation(stock, "JK")
                response = stock_response
            
        else:
            response = "Command not found!"

        data = {"text": response.encode("utf8"), "chat_id": chat_id}
        
        requests.post(url, data)

    except Exception as e:
        logger.error(e)
        response = "Exception: " + str(e)
        data = {"text": response.encode("utf8"), "chat_id": chat_id}
        requests.post(url, data)

    return {"statusCode": 200}


def check_stock(stock, ticker=""):
    try:
        stock_ticker = (stock + "." + ticker) if ticker != "" else stock
        stock = yf.Ticker(stock_ticker)
        stock_info = stock.info
        stock_fast_info = stock.fast_info

        stock_name = stock_info['longName']
        stock_last_price = stock_fast_info['last_price']
        stock_previous_price = stock_fast_info['previous_close']

        changes = stock_last_price - stock_previous_price
        changes_side = "+" if changes > 0 else "-"
        changes_percentage = changes_side + "{:.2f}%".format(round((changes / stock_previous_price) * 100), 2)

        return_on_equity = stock_info['returnOnEquity'] if "returnOnEquity" in stock_info else ""
        price_to_book = stock_info['priceToBook'] if "priceToBook" in stock_info else ""
        dividen_yield = stock_info['dividendYield'] if "dividendYield" in stock_info else ""

        response_message = ""
        response_message += stock_name + "\n\n"
        response_message += "Last Price: " + str(stock_last_price) + "\n"
        response_message += "Changes: " + changes_percentage + "\n\n"
        response_message += "Dividen Yield: " + str(dividen_yield) + "\n"
        response_message += "ROE: " + str(return_on_equity) + "\n"
        response_message += "Price to Book: " + str(price_to_book) + "\n"

        return response_message
    except Exception as e:
        return "Stock data not found!"

def check_stock_recommendation(stock, ticker=""):
    try:
        stock_ticker =(stock + "." + ticker) if ticker != "" else stock
        stock = yf.Ticker(stock_ticker)
        stock_info = stock.info

        stock_name = stock_info['longName']
        recommendation = stock_info['recommendationKey'] if "recommendationKey" in stock_info else ""
        target_low_price = stock_info['targetLowPrice'] if "targetLowPrice" in stock_info else ""
        target_mean_price = stock_info['targetMeanPrice'] if "targetMeanPrice" in stock_info else ""

        response_message = ""
        response_message += stock_name + "\n\n"
        response_message += "Recommendation: " + recommendation + "\n"
        response_message += "Target Low Price: " + str(target_low_price) + "\n"
        response_message += "Target Mean Price: " + str(target_mean_price) + "\n"

        return response_message
    except Exception as e:
        return "Stock data not found!"
    
def is_user_allowed(user_id):
    return user_id == "aryodh" or db_client.read_user_allowed_by_user_id(user_id)



    