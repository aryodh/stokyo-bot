import logging
import boto3

from boto3.dynamodb.conditions import Attr

# Static variable
import Static as static

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Dynamodb:
    def __init__(self):
        dyn_accessor = boto3.resource('dynamodb')
        self.table = dyn_accessor.Table(static.DB_STOCKS_TABLE_NAME)
        self.user_table = dyn_accessor.Table(static.DB_USERS_TABLE_NAME)

    def read_user_allowed_by_user_id(self, user_id):
        try:
            data = self.user_table.get_item(
                Key = {
                    static.USER_ID_KEY: user_id
                }
            )
            return 'Item' in data

        except Exception as err:
            logger.error("Unexpected error: %s", err)
            raise ValueError('Exception on get_item function')

    def read_subscriber_data(self):
        try:
            data = self.table.scan(
                FilterExpression = Attr(static.SUBSCRIBE_KEY).eq(True)
            )
            return data[static.ITEMS_KEY] if 'Items' in data else []

        except Exception as err:
            logger.error("Unexpected error: %s", err)
            raise ValueError('Exception on function')


    def add_allowed_user(self, user_id):
        try:
            response = self.user_table.put_item(
                TableName = static.DB_USERS_TABLE_NAME,
                Item = {
                    static.USER_ID_KEY: user_id
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
                    static.USER_ID_KEY: user_id
                }
            )
            return (data.get(static.ITEM_KEY).get(static.STOCKS_KEY) if ('Item' in data) else [])

        except Exception as err:
            logger.error("Unexpected error: %s", err)
            raise ValueError('Exception on get_item function')

    def create_user_stock(self, user_id, chat_id, stocks):
        stocks = list(dict.fromkeys(stocks))
        try:
            response = self.table.put_item(
                TableName = static.DB_STOCKS_TABLE_NAME,
                Item = {
                    static.USER_ID_KEY: user_id,
                    static.CHAT_ID_KEY: chat_id,
                    static.STOCKS_KEY: stocks,
                    static.SUBSCRIBE_KEY: False
                }
            )
        except Exception as err:
            logger.error("Unexpected error: %s", err)
        else:
            is_success = response['ResponseMetadata']['HTTPStatusCode'] == 200
            return self.response_generator(is_success, "Failed to add stock.")

    def update_user_subscribe(self, user_id, chat_id, is_subscribe):
        try:
            self.table.update_item(
                Key = {
                    static.USER_ID_KEY: user_id
                },
                ExpressionAttributeNames={
                    "#sk": static.SUBSCRIBE_KEY, 
                    "#ck": static.CHAT_ID_KEY
                },
                UpdateExpression="set #sk = :sl, #ck = :ci",
                ExpressionAttributeValues={
                    ':sl': is_subscribe,
                    ':ci': chat_id
                },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as err:
            logger.error("Unexpected error: %s", err)
            return self.response_generator(False, "Failed to update subscriber status.")

    
    def update_user_stocks(self, userId, stock_list):
        try:
            stock_list = list(dict.fromkeys(stock_list))
            stock_list = [x.upper() for x in stock_list]
            is_success = self.table.update_item(
                Key = {
                    static.USER_ID_KEY: userId
                },
                ExpressionAttributeNames={"#s": static.STOCKS_KEY},
                UpdateExpression="set #s = :sl",
                ExpressionAttributeValues={
                    ':sl': stock_list
                },
                ReturnValues="UPDATED_NEW"
            )
            return self.response_generator(is_success)
            
        except Exception as err:
            logger.error("Unexpected error: %s", err)
            return self.response_generator(False, "Failed to update user stock.")

    def add_user_stock(self, user_id, stock_list, stock):
        stock_list.append(stock)
        response = self.update_user_stocks(user_id, stock_list)
        return self.response_generator(response[static.IS_SUCCESS_KEY], "Succeed to add on your list: *" + stock + "*")

    def remove_user_stock(self, user_id, stock_list, stock):
        if stock in stock_list:
            stock_list.remove(stock)
            response = self.update_user_stocks(user_id, stock_list)
            if response[static.IS_SUCCESS_KEY]:
                return self.response_generator(True, "Succeed to remove from your list: *" + stock + "*")
            else:
                return response
        else:
            return self.response_generator(False, stock + " is not found on your list")

    def response_generator(self, is_success, message=""):
        return {
            static.IS_SUCCESS_KEY: is_success,
            static.MESSAGE_KEY: message
        }

