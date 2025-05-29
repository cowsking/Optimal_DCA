from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os

from json import dumps

load_dotenv()

client = RESTClient(api_key=os.getenv("API_KEY"), api_secret=os.getenv("API_SECRET"))

###Get account balances
#get account id
# accounts = client.get_accounts()
# print(accounts)

accounts = client.list_payment_methods()
print(accounts)

# trades = client.list_trades()
# print(trades)

# order = client.market_order_buy(client_order_id="clientOrderId", product_id="BTC-USDC", quote_size="1")
# book = client.get_products()
# print(book)
