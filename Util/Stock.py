import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))

import yfinance as yf

import Util.Message as message

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check_stock(stock, ticker, chat_id):
    try:
        stock_ticker = (stock + "." + ticker) if ticker != "" else stock
        stock = yf.Ticker(stock_ticker)
        stock_info = stock.info
        stock_fast_info = stock.fast_info

        stock_name = stock_info['longName']
        stock_last_price = stock_fast_info['last_price']
        stock_previous_price = stock_fast_info['previous_close']

        changes = stock_last_price - stock_previous_price
        changes_side = "+" if changes > 0 else ""
        changes_percentage = changes_side + "{:.2f}%".format((changes / stock_previous_price) * 100)

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

    except Exception as e:
        logger.error(e)
        response_message = "Stock data not found!"
    
    return message.send_message(response_message, chat_id)

    

def check_stock_recommendation(stock, ticker, chat_id):
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

    except Exception as e:
        logger.error(e)
        response_message = "Stock data not found!"
    
    return message.send_message(response_message, chat_id)