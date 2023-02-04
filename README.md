# stokyo-bot
Stokyo is a bot purposing on Stock related stuff by utilizing Yahoo Finance data.
Telegram bot: @stokyo_bot

## Usage / Command
- `/checkmyusername`: Checking your telegram username
- `/adduserpermission <USERNAME>`: Adding username to the whitelist user
- `/addstock <TICKER>`: Adding stock to your wishlist
- `/watchlist`: Showing stocks that have been you added
- `/checkstock <TICKER>`: Get information related to stock price
- `/checkstockidx <TICKER>`: Get information related to stock price specific on IDX
- `/stockrecom <TICKER>`: Get recommendation for the stock
- `/stockrecomidx <TICKER>`: Get recommendation for the stock specific on IDX

## Stack 
- AWS Lambda
- API Gateway
- DynamoDB

You can use the free tier for both of them since AWS providing free 100k invocation to Lambda and 1M hit on the API Gateway
