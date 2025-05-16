from coinbase.rest import RESTClient

api_key = ""
api_secret = ""

from json import dumps


client = RESTClient(api_key=api_key, api_secret=api_secret)

###Get account balances

accounts = client.list_payment_methods()
print(accounts)

# trades = client.list_trades()
# print(trades)

# order = client.market_order_buy(client_order_id="clientOrderId", product_id="BTC-USDC", quote_size="1")
# book = client.get_products()
# print(book)
client.deposit(payment_method_id="faeea233-4182-58f6-b55d-35da447bd79f", amount="1", currency="USD")