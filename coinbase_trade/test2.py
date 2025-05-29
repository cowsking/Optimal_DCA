import requests
from coinbase.rest import RESTClient
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os

load_dotenv()

def get_weights(coins, fiat_currency):
    market_cap = {}
    try:
        # CoinGecko API
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'sparkline': False
        })
        assets = response.json()
        coin_data = {}
        for coin in assets:
            coin_data[coin['symbol'].upper()] = coin
        for c in coins:
            market_cap[c] = float(coin_data[c]['market_cap'])
    except HTTPError as e:
        print(f"caught exception when fetching ticker for {c} with name={coins[c]['name']}")
        raise e

    total_market_cap = sum(market_cap.values())
    weights = {}
    for c in coins:
        weights[c] = market_cap[c] / total_market_cap
    print("coin weights:")
    for w in weights:
        print(f"  {w}: {weights[w]:.4f}")
    print()
    
    return weights

def get_products_info(client, coins_dict, fiat_currency):
    # coins_dict is the original dict from args.coins
    # We'll update it with minimum_order_size
    try:
        products_response = client.get_products(product_type="SPOT")
        if products_response and products_response.products:
            for p in products_response.products:
                # print("p.base_currency_id", p.base_currency_id)
                # print("p.quote_currency_id", p.quote_currency_id)
                base_currency = p.base_currency_id
                # print("base_currency", base_currency)
                # print("p", p)
                if base_currency in coins_dict and p.quote_currency_id == fiat_currency:
                    # Use quote_min_size for minimum order value in fiat
                    # The original script used "min_market_funds"
                    # print("p.quote_min_size", p.quote_min_size)
                    # print("p",p)
                    coins_dict[base_currency]["minimum_order_size"] = float(p.quote_min_size) 
        else:
            print("Warning: Could not retrieve products or no products found.")
    except HTTPError as e:
        print(f"HTTPError fetching products: {e}")
        raise
    except Exception as e:
        print(f"Error fetching products: {e}")
        raise
    return coins_dict

def get_prices(client, coins_symbols_list, fiat_currency):
    prices = {}
    for c_symbol in coins_symbols_list:
        product_id = f"{c_symbol}-{fiat_currency}"
        try:
            ticker_response = client.get_product(product_id=product_id)
            if ticker_response and ticker_response.price:
                print(f"{c_symbol} ticker price: {ticker_response.price}")
                prices[c_symbol] = float(ticker_response.price)
            else:
                raise Exception(f"No price available for {c_symbol} or invalid response. Ticker: {ticker_response}")
        except HTTPError as e:
            print(f"HTTPError fetching ticker for {product_id}: {e}")
            raise
        except Exception as e:
            print(f"Error fetching ticker for {product_id}: {e}")
            # Decide if you want to raise or try to continue with other coins
            raise # Or prices[c_symbol] = None and handle later
    return prices

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = RESTClient(api_key=api_key, api_secret=api_secret)
coins = {
      "BTC":{
        "name":"Bitcoin",
        "withdrawal_address":"",
        "external_balance":0
      },
      "ETH":{
        "name":"Ethereum",
        "withdrawal_address":"",
        "external_balance":0
      },
      "LTC":{
        "name":"Litecoin",
        "withdrawal_address":"",
        "external_balance":0
      }
    }
print(get_prices(client, coins, "USDC"))