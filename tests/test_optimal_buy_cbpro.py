#!/usr/bin/env python3
import pytest
import math
import json
from coinbase.rest import RESTClient

from optimal_buy_cbpro import optimal_buy_cbpro
api_key = "organizations/9fb9f9ad-b496-494e-9fdd-40fc978aa72c/apiKeys/4810e4bf-d9dd-41d4-93ed-ea99f1e818ab"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIB0caGXzcMOsSOENNDwjqYUiZBt11aU24PAXkYUHdFvfoAoGCCqGSM49\nAwEHoUQDQgAEbreKJ/v/rzdSE4aQNwzXbA3elcJDTd8zzj7cSAYTdhToqg5tWNWi\n/6MwkG4zH1oiuH3rhbkZJ7IGMOz5nemQNA==\n-----END EC PRIVATE KEY-----\n"



# client = RESTClient(api_key=api_key, api_secret=api_secret)

@pytest.fixture
def coins():
    coins = """
    {
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
      "ADA":{
        "name":"Cardano",
        "withdrawal_address":"",
        "external_balance":0
      }
    }"""
    return json.loads(coins)


@pytest.fixture
def args():
    class Args:
        order_count = 5
        starting_discount = 0.005
        discount_step = 0.001

    return Args()


def test_get_weights(coins):
    # weights = optimal_buy_cbpro.get_weights(coins, "USD")
    # assert "BTC" in weights
    # assert weights["BTC"] == 1
    print("\nCoins dictionary:")
    print(json.dumps(coins, indent=2))
    
    weights = optimal_buy_cbpro.get_weights(coins, "USD")
    print("\nWeights returned:")
    print(json.dumps(weights, indent=2))
    
    assert "BTC" in weights
    assert 0 <= weights["BTC"] <= 1

def test_get_products(coins):
    print("\nCoins dictionary:")
    print(json.dumps(coins, indent=2))
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    products = optimal_buy_cbpro.get_products_info(client, coins, "USD")
    assert len(products) >= 0
    assert "BTC" in [product["base_currency"] for product in products]


def test_get_prices(coins):
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    prices = optimal_buy_cbpro.get_prices(client, coins, "USD")
    assert len(prices) >= 0
    assert "BTC" in prices
    assert prices["BTC"] >= 1


def test_generate_orders(coins, args):
    orders = optimal_buy_cbpro.generate_buy_orders(coins, "BTC", args, 500, 5000)
    print("\nOrders returned:")
    print(json.dumps(orders, indent=2))
    assert len(orders) == 5
    assert orders[0]["price"] == 4975.0
    assert orders[1]["price"] == 4970.0
    assert orders[2]["price"] == 4965.0
    assert orders[3]["price"] == 4960.0
    assert orders[4]["price"] == 4955.0

    assert math.isclose(
        sum([o["size"] * o["price"] for o in orders]), 500, abs_tol=0.01
    )

    assert math.isclose(orders[0]["size"], 0.020100502, abs_tol=0.0000001)
    assert math.isclose(orders[1]["size"], 0.020120724, abs_tol=0.0000001)
    assert math.isclose(orders[2]["size"], 0.020140987, abs_tol=0.0000001)
    assert math.isclose(orders[3]["size"], 0.020161290, abs_tol=0.0000001)
    assert math.isclose(orders[4]["size"], 0.020181634, abs_tol=0.0000001)


def test_generate_orders_rounding(coins, args):
    orders = optimal_buy_cbpro.generate_buy_orders(coins, "BTC", args, 1000.0, 4155.42)
    print("\nOrders returned:")
    print(json.dumps(orders, indent=2))
    assert len(orders) == 5
    assert orders[0]["price"] == 4134.64
    assert orders[1]["price"] == 4130.48
    assert orders[2]["price"] == 4126.33
    assert orders[3]["price"] == 4122.17
    assert orders[4]["price"] == 4118.02

    assert math.isclose(
        sum([o["size"] * o["price"] for o in orders]), 1000.0, abs_tol=0.01
    )

    assert math.isclose(orders[0]["size"], 0.048371805, abs_tol=0.0000001)
    assert math.isclose(orders[1]["size"], 0.048420522, abs_tol=0.0000001)
    assert math.isclose(orders[2]["size"], 0.048469220, abs_tol=0.0000001)
    assert math.isclose(orders[3]["size"], 0.048518134, abs_tol=0.0000001)
    assert math.isclose(orders[4]["size"], 0.048567029, abs_tol=0.0000001)

    for o in orders:
        assert o["size"] * o["price"] <= 201.0


def test_generate_orders_rounding2(coins, args):
    args.starting_discount = 0.02
    args.discount_step = 0.00725

    orders = optimal_buy_cbpro.generate_buy_orders(coins, "BTC", args, 400.0, 3394.99)
    assert len(orders) == 5
    assert orders[0]["price"] == 3327.09
    assert orders[1]["price"] == 3302.47
    assert orders[2]["price"] == 3277.86
    assert orders[3]["price"] == 3253.24
    assert orders[4]["price"] == 3228.63

    assert math.isclose(
        sum([o["size"] * o["price"] for o in orders]), 400.0, abs_tol=0.01
    )

    assert math.isclose(orders[0]["size"], 0.024045036, abs_tol=0.0000001)
    assert math.isclose(orders[1]["size"], 0.02422424, abs_tol=0.0000001)
    assert math.isclose(orders[2]["size"], 0.02440615, abs_tol=0.0000001)
    assert math.isclose(orders[3]["size"], 0.02459080, abs_tol=0.0000001)
    assert math.isclose(orders[4]["size"], 0.02477827, abs_tol=0.0000001)

    for o in orders:
        assert o["size"] * o["price"] <= 100.0


def test_generate_orders_rounding3(coins, args):
    args.starting_discount = 0.02
    args.discount_step = 0.00725

    orders = optimal_buy_cbpro.generate_buy_orders(coins, "BTC", args, 500.0, 3630.51)
    assert len(orders) == 5
    assert orders[0]["price"] == 3557.89
    assert orders[1]["price"] == 3531.57
    assert orders[2]["price"] == 3505.25
    assert orders[3]["price"] == 3478.93
    assert orders[4]["price"] == 3452.61

    assert math.isclose(
        sum([o["size"] * o["price"] for o in orders]), 500.0, abs_tol=0.01
    )

    assert math.isclose(orders[0]["size"], 0.02810647, abs_tol=0.0000001)
    assert math.isclose(orders[1]["size"], 0.02831595, abs_tol=0.0000001)
    assert math.isclose(orders[2]["size"], 0.02852858, abs_tol=0.0000001)
    assert math.isclose(orders[3]["size"], 0.02874442, abs_tol=0.0000001)
    assert math.isclose(orders[4]["size"], 0.02896355, abs_tol=0.0000001)

    for o in orders:
        assert o["size"] * o["price"] <= 100.0


def test_generate_orders_rounding4(coins, args):
    args.starting_discount = 0.02
    args.discount_step = 0.00725

    orders = optimal_buy_cbpro.generate_buy_orders(coins, "BTC", args, 500.0, 3577.97)
    assert len(orders) == 5
    assert orders[0]["price"] == 3506.41
    assert orders[1]["price"] == 3480.47
    assert orders[2]["price"] == 3454.53
    assert orders[3]["price"] == 3428.58
    assert orders[4]["price"] == 3402.64

    assert math.isclose(
        sum([o["size"] * o["price"] for o in orders]), 500.0, abs_tol=0.01
    )

    assert math.isclose(orders[0]["size"], 0.02851920, abs_tol=0.0000001)
    assert math.isclose(orders[1]["size"], 0.02873175, abs_tol=0.0000001)
    assert math.isclose(orders[2]["size"], 0.02894750, abs_tol=0.0000001)
    assert math.isclose(orders[3]["size"], 0.02916659, abs_tol=0.0000001)
    assert math.isclose(orders[4]["size"], 0.02938895, abs_tol=0.0000001)

    for o in orders:
        assert o["size"] * o["price"] <= 100
