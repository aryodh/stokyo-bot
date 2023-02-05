import os

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

USER_ID_KEY = 'userId'
CHAT_ID_KEY = 'chatId'
STOCKS_KEY = 'stocks'
SUBSCRIBE_KEY = "isSubscribe"
ITEM_KEY = 'Item'
ITEMS_KEY = 'Items'

IS_SUCCESS_KEY = "is_success"
MESSAGE_KEY = "message"

DB_STOCKS_TABLE_NAME = 'user_stocks'
DB_USERS_TABLE_NAME = 'allowed_users'