from coinbase.rest import RESTClient

api_key = "organizations/9fb9f9ad-b496-494e-9fdd-40fc978aa72c/apiKeys/4810e4bf-d9dd-41d4-93ed-ea99f1e818ab"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIB0caGXzcMOsSOENNDwjqYUiZBt11aU24PAXkYUHdFvfoAoGCCqGSM49\nAwEHoUQDQgAEbreKJ/v/rzdSE4aQNwzXbA3elcJDTd8zzj7cSAYTdhToqg5tWNWi\n/6MwkG4zH1oiuH3rhbkZJ7IGMOz5nemQNA==\n-----END EC PRIVATE KEY-----\n"

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