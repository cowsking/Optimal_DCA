#!/usr/bin/env python3
import pytest
import json
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coinbase.rest import RESTClient
from optimal_buy_cbpro.optimal_buy_cbpro import buy, get_weights
from optimal_buy_cbpro.history import get_session

# WARNING: This test uses real money. Use with extreme caution.
# Make sure you understand the risks and have proper API permissions set up.

# Your API credentials


# Test configuration with multiple coins
TEST_COINS_CONFIG = {
    "BTC": {
        "name": "Bitcoin",
        "withdrawal_address": None,
        "external_balance": 0
    },
    "ETH": {
        "name": "Ethereum",
        "withdrawal_address": None,
        "external_balance": 0
    },
    "ADA": {
        "name": "Cardano",
        "withdrawal_address": None,
        "external_balance": 0
    }
}
# TEST_COINS_CONFIG = {
#     "JASMY": {
#         "name": "JasmyCoin",
#         "withdrawal_address": None,
#         "external_balance": 0,
#         "minimum_order_size": 1
#     },
# }
class TestArgs:
    def __init__(self):
        self.fiat_currency = "USD"
        self.base_fee = 0.006
        self.withdrawal_threshold = 25.0
        self.starting_discount = 0.005  # 0.5% discount
        self.discount_step = 0.001      # 0.1% step
        self.order_count = 5            # Create 5 orders per coin
        self.max_retries = 1

def test_real_buy():
    """
    WARNING: This test uses real money.
    It will place real buy orders with small amounts for BTC, ETH, and ADA.
    Make sure you understand the risks before running this test.
    """
    print("\nWARNING: This test will use real money!")
    print("It will place real buy orders for BTC, ETH, and ADA with small amounts.")
    print("Make sure you understand the risks before proceeding.")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with real money testing? (yes/no): ")
    if response.lower() != 'yes':
        print("Test cancelled.")
        return
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    # Initialize client and session
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    db_session = get_session("sqlite:///test_cbpro_history.db")

    try:
        # Get current account balance
        accounts = client.get_accounts()
        usd_balance = None
        for account in accounts.accounts:
            if account.currency == "USD":
                # Get the account as a dictionary
                account_dict = account.to_dict()
                
                # Access the balance from the dictionary
                if 'available_balance' in account_dict:
                    balance_dict = account_dict['available_balance']
                    if isinstance(balance_dict, dict) and 'value' in balance_dict:
                        usd_balance = float(balance_dict['value'])
                    else:
                        usd_balance = float(balance_dict)
                break

        if not usd_balance:
            print("No USD balance found. Test cancelled.")
            return

        print(f"\nCurrent USD balance: ${usd_balance:.2f}")

        # Get market cap weights for the coins
        print("\nFetching market cap weights...")
        weights = get_weights(list(TEST_COINS_CONFIG.keys()), "USD")
        print("\nMarket cap weights:")
        for coin, weight in weights.items():
            print(f"{coin}: {weight:.4f}")

        # Get current prices
        print("\nFetching current prices...")
        prices = {}
        for coin in TEST_COINS_CONFIG.keys():
            product_id = f"{coin}-USD"
            ticker = client.get_product(product_id=product_id)
            if ticker and ticker.price:
                prices[coin] = float(ticker.price)
                print(f"{coin} current price: ${prices[coin]:.2f}")

        # Confirm the amount to test with
        test_amount = min(30.0, usd_balance * 0.1)  # Use at most $30 or 10% of balance
        print(f"\nSuggested test amount: ${test_amount:.2f}")
        response = input(f"Do you want to proceed with ${test_amount:.2f}? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Test cancelled.")
            return

        # Create test arguments
        args = TestArgs()
        
        # Calculate and print total allocation
        total_allocated = 0
        print("\nMoney Allocation Summary:")
        print("------------------------")
        for coin, weight in weights.items():
            amount = test_amount * weight
            total_allocated += amount
            print(f"{coin}: ${amount:.2f} ({weight*100:.1f}% of ${test_amount:.2f})")
        print(f"Total allocated: ${total_allocated:.2f}")
        print(f"Remaining balance: ${(usd_balance - total_allocated):.2f}")
        
        # Print allocation vs. minimum order size for each coin
        print("\nOrder Placement Debug Info:")
        for coin, weight in weights.items():
            amount = test_amount * weight
            min_order = TEST_COINS_CONFIG[coin].get("minimum_order_size", 0.01)
            print(f"{coin}: allocated ${amount:.2f}, minimum order size ${min_order:.2f}")
            if amount < min_order:
                print(f"  -> Skipping {coin}: allocated < minimum order size")
            else:
                print(f"  -> Will place orders for {coin}")

        # Final confirmation
        print("\nPlease review the allocation above.")
        response = input("Do you want to proceed with these orders? (yes/no): ")
        if response.lower() != 'yes':
            print("Test cancelled.")
            return
        
        # Run the buy function
        print("\nExecuting buy function...")
        print(TEST_COINS_CONFIG)
        print(args)
        buy(args, TEST_COINS_CONFIG, client, db_session)
        
        print("\nTest completed. Check your Coinbase account for the orders.")
        print("Orders were distributed according to market cap weights:")
        for coin, weight in weights.items():
            amount = test_amount * weight
            print(f"{coin}: ${amount:.2f}")

    except Exception as e:
        print(f"\nError during test: {e}")
        raise
    finally:
        db_session.close()

if __name__ == "__main__":
    load_dotenv()
    test_real_buy() 