import Util.Message as message

def add_user_stock(db_client, username, stocks, chat_id):
    if len(stocks) > 1:
        stocks = [x.upper() for x in stocks]
        user_stock_list = db_client.read_user_stock_list(username)
        if user_stock_list is None or len(user_stock_list) == 0:
            isSuccess = db_client.create_user_stock(username, chat_id, stocks)
        else:
            user_stock_list += stocks
            isSuccess = db_client.update_user_stocks(username, user_stock_list)

        if isSuccess:
            response = (', '.join(stocks) + " is success to add!\nSee your watchlist: /watchlist")
        else:
            response = "Failed to add stocks!"
    elif stocks:
        stock = stocks[0].upper()
        user_stock_list = db_client.read_user_stock_list(username)
        if user_stock_list is None or len(user_stock_list) == 0:
            isSuccess = db_client.create_user_stock(username, chat_id, stocks)
        else:
            isSuccess = db_client.add_user_stock(username, user_stock_list, stock)
        response = (stock + " is success to add!\nSee your watchlist: /watchlist") if isSuccess else "Error adding stock.\nPlease try again."
    else:
        response = "Please define the stock you want to add"
    return message.send_message(response, chat_id)

def remove_user_stock(db_client, username, stocks, chat_id):
    if stocks:
        stock = stocks[1].upper()
        user_stock_list = db_client.read_user_stock_list(username)
        if len(user_stock_list) > 0:
            isSuccess = db_client.remove_user_stock(username, user_stock_list, stock)
            response = ("*" + stock + "* is success to remove!\nSee your watchlist: /watchlist" if isSuccess else "Error removing stock.\nPlease try again.")
        else:
            response = "Watch list already empty!"
    else:
        response = "Please define the stock you want to remove"
        
    return message.send_message(response, chat_id)

def view_watchlist(db_client, username, chat_id):
    stocks =  db_client.read_user_stock_list(username)
    if stocks is None or len(stocks) == 0:
        response = "Your watchlist is empty!"
    else:
        response = "Your watchlist:"
        for stock in stocks:
            response += "\n• " + stock 
    
    return message.send_message(response, chat_id)
