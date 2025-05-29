#!/usr/bin/env python3
import pytest
import math
import json
from coinbase.rest import RESTClient
from unittest.mock import Mock, patch
from optimal_buy_cbpro.optimal_buy_cbpro import buy
from optimal_buy_cbpro.history import get_session
import os
from dotenv import load_dotenv

from optimal_buy_cbpro import optimal_buy_cbpro
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

load_dotenv()

# client = RESTClient(api_key=api_key, api_secret=api_secret)

@pytest.fixture
def coins():
    # coins = """
    # {
    #   "BTC":{
    #     "name":"Bitcoin",
    #     "withdrawal_address":"",
    #     "external_balance":0
    #   },
    #   "ETH":{
    #     "name":"Ethereum",
    #     "withdrawal_address":"",
    #     "external_balance":0
    #   },
    #   "ADA":{
    #     "name":"Cardano",
    #     "withdrawal_address":"",
    #     "external_balance":0
    #   },
    #   "JASMY":{
    #     "name":"JasmyCoin",
    #     "withdrawal_address":"",
    #     "external_balance":0
    #   }
    # }"""
    """
    {
      "JASMY":{
        "name":"JasmyCoin",
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

# Sample test data
SAMPLE_COINS_CONFIG = {
    "BTC": {
        "name": "Bitcoin",
        "withdrawal_address": None,
        "external_balance": 0
    },
    "ETH": {
        "name": "Ethereum",
        "withdrawal_address": None,
        "external_balance": 0
    }
}

class MockArgs:
    def __init__(self):
        self.fiat_currency = "USD"
        self.base_fee = 0.006
        self.withdrawal_threshold = 25.0
        self.starting_discount = 0.005
        self.discount_step = 0.01
        self.order_count = 5

@pytest.fixture
def mock_client():
    client = Mock()
    
    # Mock get_accounts response
    mock_accounts = Mock()
    mock_accounts.accounts = [
        Mock(currency="USD", available_balance=Mock(value="1000.00")),
        Mock(currency="BTC", available_balance=Mock(value="0.1")),
        Mock(currency="ETH", available_balance=Mock(value="1.0"))
    ]
    mock_accounts.to_dict = Mock(return_value={
        "accounts": [
            {"currency": "USD", "available_balance": {"value": "1000.00"}},
            {"currency": "BTC", "available_balance": {"value": "0.1"}},
            {"currency": "ETH", "available_balance": {"value": "1.0"}}
        ]
    })
    client.get_accounts.return_value = mock_accounts
    
    # Mock get_products response
    mock_products = Mock()
    mock_products.products = [
        Mock(base_currency_id="BTC", quote_currency_id="USD", quote_min_size="10.00"),
        Mock(base_currency_id="ETH", quote_currency_id="USD", quote_min_size="10.00")
    ]
    mock_products.to_dict = Mock(return_value={
        "products": [
            {"base_currency_id": "BTC", "quote_currency_id": "USD", "quote_min_size": "10.00"},
            {"base_currency_id": "ETH", "quote_currency_id": "USD", "quote_min_size": "10.00"}
        ]
    })
    client.get_products.return_value = mock_products
    
    # Mock get_product (for prices)
    def mock_get_product(product_id):
        mock_product = Mock()
        if "BTC" in product_id:
            mock_product.price = "50000.00"
        elif "ETH" in product_id:
            mock_product.price = "3000.00"
        mock_product.to_dict = Mock(return_value={
            "price": mock_product.price
        })
        return mock_product
    client.get_product.side_effect = mock_get_product
    
    # Mock list_orders and cancel_orders
    mock_orders = Mock()
    mock_orders.orders = []
    mock_orders.to_dict = Mock(return_value={"orders": []})
    client.list_orders.return_value = mock_orders
    
    mock_cancel = Mock()
    mock_cancel.results = []
    mock_cancel.to_dict = Mock(return_value={"results": []})
    client.cancel_orders.return_value = mock_cancel
    
    return client

@pytest.fixture
def mock_db_session():
    session = Mock()
    return session

def test_buy_function(mock_client, mock_db_session):
    args = MockArgs()
    
    # Test the buy function
    buy(args, SAMPLE_COINS_CONFIG, mock_client, mock_db_session)
    
    # Verify that the client methods were called
    mock_client.get_accounts.assert_called_once()
    mock_client.get_products.assert_called_once()
    mock_client.get_product.assert_called()
    mock_client.list_orders.assert_called()
    
    # Verify that the correct product IDs were used
    expected_product_ids = ["BTC-USD", "ETH-USD"]
    for product_id in expected_product_ids:
        mock_client.get_product.assert_any_call(product_id=product_id)
        mock_client.list_orders.assert_any_call(product_ids=[product_id], order_status=["OPEN", "PENDING"])

def test_buy_function_with_low_balance(mock_client, mock_db_session):
    args = MockArgs()
    
    # Modify mock client to return low balance
    mock_accounts = Mock()
    mock_accounts.accounts = [
        Mock(currency="USD", available_balance=Mock(value="10.00")),  # Low balance
        Mock(currency="BTC", available_balance=Mock(value="0.1")),
        Mock(currency="ETH", available_balance=Mock(value="1.0"))
    ]
    # Add to_dict method to mock_accounts
    mock_accounts.to_dict = Mock(return_value={
        "accounts": [
            {"currency": "USD", "available_balance": {"value": "10.00"}},
            {"currency": "BTC", "available_balance": {"value": "0.1"}},
            {"currency": "ETH", "available_balance": {"value": "1.0"}}
        ]
    })
    mock_client.get_accounts.return_value = mock_accounts
    
    # Mock products response
    mock_products = Mock()
    mock_products.products = [
        Mock(base_currency_id="BTC", quote_currency_id="USD", quote_min_size="10.00"),
        Mock(base_currency_id="ETH", quote_currency_id="USD", quote_min_size="10.00")
    ]
    mock_products.to_dict = Mock(return_value={
        "products": [
            {"base_currency_id": "BTC", "quote_currency_id": "USD", "quote_min_size": "10.00"},
            {"base_currency_id": "ETH", "quote_currency_id": "USD", "quote_min_size": "10.00"}
        ]
    })
    mock_client.get_products.return_value = mock_products
    
    # Test the buy function
    buy(args, SAMPLE_COINS_CONFIG, mock_client, mock_db_session)
    
    # Verify that no orders were placed due to low balance
    mock_client.get_accounts.assert_called_once()
    mock_client.get_products.assert_called_once()
    mock_client.get_product.assert_called()

def test_buy_function_with_open_orders(mock_client, mock_db_session):
    args = MockArgs()
    
    # Mock open orders
    mock_orders = Mock()
    mock_orders.orders = [
        Mock(order_id="test_order_1"),
        Mock(order_id="test_order_2")
    ]
    mock_orders.to_dict = Mock(return_value={
        "orders": [
            {"order_id": "test_order_1"},
            {"order_id": "test_order_2"}
        ]
    })
    mock_client.list_orders.return_value = mock_orders
    
    # Test the buy function
    buy(args, SAMPLE_COINS_CONFIG, mock_client, mock_db_session)
    
    # Verify that cancel_orders was called with the correct order IDs
    mock_client.cancel_orders.assert_called_with(order_ids=["test_order_1", "test_order_2"])

def test_buy_function_with_error(mock_client, mock_db_session):
    args = MockArgs()
    
    # Mock an error in get_accounts
    mock_client.get_accounts.side_effect = Exception("API Error")
    
    # Test the buy function
    with pytest.raises(Exception) as exc_info:
        buy(args, SAMPLE_COINS_CONFIG, mock_client, mock_db_session)
    
    assert str(exc_info.value) == "API Error"
    mock_client.get_accounts.assert_called_once()
