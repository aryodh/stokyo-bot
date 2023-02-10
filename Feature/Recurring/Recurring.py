import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import requests
import Util.Message as message_util
import yfinance as yf

# Static variable
import Static as static

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lunch_update(db_client):
    subscriber_list = db_client.read_subscriber_data()
    for subscriber in subscriber_list:
        try:
            stocks = subscriber[static.STOCKS_KEY]
            chat_id_target = subscriber[static.CHAT_ID_KEY]
            username = subscriber[static.USER_ID_KEY]

            message = generate_lunch_update_message(username, stocks)
            message_util.send_message_without_return(message, chat_id_target)

        except Exception as e:
            logger.error(e)
    
    return {"statusCode": 200}

def generate_lunch_update_message(username, stocks):
    message = "Watchlist lunch update for: @" + username
    message += "\n\n"

    try:
        for stock in stocks:
            current_stock = yf.Ticker(stock if "." in stock else (stock + ".JK"))
            try:
                stock_fast_info = current_stock.fast_info
            except Exception as e:
                stock_fast_info = {}
            
            stock_last_price = stock_fast_info['last_price'] if "last_price" in stock_fast_info else "Not found"
            stock_previous_price = stock_fast_info['previous_close'] if "previous_close" in stock_fast_info else "Not found"

            if stock_fast_info:
                changes = stock_last_price - stock_previous_price
                changes_side = "+" if changes > 0 else ""
                changes_percentage = changes_side + "{:.2f}%".format((changes / stock_previous_price) * 100)
            else:
                changes_percentage = "Not found"

            message += "*" + stock + "*\n"
            message += "- last price: " + str(stock_last_price) +"\n"
            message += "- changes: " + changes_percentage +"\n"
            message += "\n"

    except Exception as e:
        logger.error(e)
    
    return message