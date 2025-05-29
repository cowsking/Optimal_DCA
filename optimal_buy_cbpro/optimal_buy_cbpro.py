#!/usr/bin/env python3

from coinbase.rest import RESTClient
import argparse
import sys
import math
import time
import dateutil.parser
import json
import requests
from datetime import datetime, timezone # Added for created_at
from decimal import Decimal, getcontext, ROUND_DOWN

# Assuming history.py is in the same directory or Python path
# and defines Order, Deposit, Withdrawal, get_session SQLAlchemy models
from .history import Order, Deposit, Withdrawal, get_session
from requests.exceptions import HTTPError

# Use different precision for different coins
DECIMAL_PRECISION_MAP = {
    'BTC': Decimal('0.00001'),  # 6 decimal places for BTC
    'ETH': Decimal('0.00001'),  # 6 decimal places for ETH
    'JASMY': Decimal('1'),     # 1 decimal place for JASMY
}

# Price precision can be different from size precision for some coins
PRICE_PRECISION_MAP = {
    'BTC': Decimal('0.01'),      # 2 decimal places for BTC price
    'ETH': Decimal('0.01'),      # 2 decimal places for ETH price
    'JASMY': Decimal('0.00001'), # 6 decimal places for JASMY price
}

DEFAULT_PRECISION = Decimal('0.00001')  # Default 4 decimal places
DEFAULT_PRICE_PRECISION = Decimal('0.01')  # Default 2 decimal places for price

def get_decimal_precision(coin_symbol):
    return DECIMAL_PRECISION_MAP.get(coin_symbol.upper(), DEFAULT_PRECISION)

def get_price_precision(coin_symbol):
    return PRICE_PRECISION_MAP.get(coin_symbol.upper(), DEFAULT_PRICE_PRECISION)

def get_weights(coins, fiat_currency):
    market_cap = {}
    try:
        # CoinGecko API - This part remains unchanged as it's an external API call
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={
            'vs_currency': 'usd', # Assuming USD for market cap comparison, adjust if needed
            'order': 'market_cap_desc',
            'per_page': 200, # Fetching enough coins to likely find those in user's list
            'page': 1,
            'sparkline': False
        })
        response.raise_for_status() # Check for HTTP errors
        assets = response.json()
        coin_data = {}
        for coin_info in assets:
            coin_data[coin_info['symbol'].upper()] = coin_info
        
        found_all_coins = True
        for c in coins:
            if c.upper() in coin_data:
                market_cap[c.upper()] = float(coin_data[c.upper()]['market_cap'])
            else:
                print(f"Warning: Market cap data not found for {c} on CoinGecko.")
                found_all_coins = False
                # Fallback or error handling:
                # Option 1: Assign a zero or very small market cap (might skew weights)
                # market_cap[c.upper()] = 0 
                # Option 2: Skip this coin for weighting (adjust logic below)
                # Option 3: Raise an error
                # For this example, let's try to proceed but warn the user
                # and potentially exclude it from total_market_cap calculation if 0.
                market_cap[c.upper()] = 0 # Or handle as an error


        if not found_all_coins and not any(market_cap.values()): # if all coins failed to fetch
             raise Exception("Could not fetch market cap data for any of the specified coins from CoinGecko.")

    except HTTPError as e:
        print(f"Caught HTTP exception when fetching market data from CoinGecko: {e}")
        raise e
    except requests.exceptions.RequestException as e:
        print(f"Caught requests exception when fetching market data from CoinGecko: {e}")
        raise e
    except KeyError as e:
        print(f"KeyError while processing CoinGecko data (likely missing field for a coin): {e}")
        raise e
    except ValueError as e: # For float conversion issues
        print(f"ValueError while processing CoinGecko data: {e}")
        raise e


    total_market_cap = sum(market_cap.values())
    if total_market_cap == 0 and market_cap: # Avoid division by zero if all found coins have 0 mcap
        print("Warning: Total market cap is zero. Weights cannot be determined accurately.")
        weights = {c: 0 for c in coins} # Or assign equal weights, or handle as error
    else:
        weights = {}
        for c in coins:
            weights[c.upper()] = market_cap[c.upper()] / total_market_cap if total_market_cap > 0 else 0
            
    print("Coin weights:")
    for w in weights:
        print(f"  {w}: {weights[w]:.4f}")
    print()
    
    return weights


def deposit(args, client, db_session):
    if args.amount is None:
        print("Please specify deposit amount with `--amount`")
        sys.exit(1)
    if args.payment_method_id is None:
        print("Please provide a payment method ID with `--payment-method-id`")
        sys.exit(1)

    print(f"Performing deposit, amount={args.amount} {args.fiat_currency}")
    
    # NOTE: The coinbase-advanced-py SDK version reflected in the provided files
    # does not show a direct method in RESTClient for making fiat deposits
    # from a payment_method_id (like bank).
    # This functionality might be available through a different API,
    # via the Coinbase website/app, or a future/different version of the SDK.
    # The original script's client.deposit(...) call cannot be directly translated.
    print("Fiat deposit functionality via payment_method_id is not directly available in this SDK version.")
    print("Please handle deposits manually or explore other Coinbase APIs/SDKs for this feature.")
    
    # Assuming the old `deposit` response structure and DB logging.
    # If an alternative method is found, this part would need to be adapted.
    # For now, this part of the function will not execute.
    deposit_response_simulated = {
        # "id": "simulated_deposit_id_123",
        # "payout_at": datetime.now(timezone.utc).isoformat() 
    } # Example structure

    if "id" in deposit_response_simulated: # This block will not run with the current placeholder
        # db_session.add(
        #     Deposit(
        #         payment_method_id=args.payment_method_id,
        #         amount=args.amount,
        #         currency=args.fiat_currency,
        #         payout_at=dateutil.parser.parse(deposit_response_simulated["payout_at"]),
        #         coinbase_deposit_id=deposit_response_simulated["id"], # Renamed field
        #     )
        # )
        # db_session.commit()
        pass


def get_products_info(client, coins_dict, fiat_currency):
    # coins_dict is the original dict from args.coins
    # We'll update it with minimum_order_size
    try:
        products_response = client.get_products(product_type="SPOT")
        if products_response and products_response.products:
            for p in products_response.products:
                base_currency = p.base_currency_id
                if base_currency in coins_dict and p.quote_currency_id == fiat_currency:
                    # Use quote_min_size for minimum order value in fiat
                    # The original script used "min_market_funds"
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


def get_external_balance(coins_dict, coin_symbol):
    # coins_dict is the dictionary holding info for each coin, including external_balance
    external_balance = float(coins_dict.get(coin_symbol, {}).get("external_balance", 0))
    if external_balance > 0:
        print(f"Including external balance of {external_balance} {coin_symbol}")
    return external_balance


def get_fiat_balances(args, coins_dict, accounts_response, withdrawn_balances, prices):
    # coins_dict holds coin configuration, accounts_response is from client.get_accounts()
    balances = {}
    if accounts_response and accounts_response.accounts:
        for acc in accounts_response.accounts:
            currency = acc.currency
            if currency == args.fiat_currency:
                # Handle the dictionary structure of available_balance
                if hasattr(acc, 'available_balance'):
                    if isinstance(acc.available_balance, dict):
                        balances[args.fiat_currency] = float(acc.available_balance.get('value', 0))
                    else:
                        balances[args.fiat_currency] = float(acc.available_balance)
            elif currency in coins_dict: # Check against configured coins
                # Handle the dictionary structure of available_balance
                if hasattr(acc, 'available_balance'):
                    if isinstance(acc.available_balance, dict):
                        balance = float(acc.available_balance.get('value', 0))
                    else:
                        balance = float(acc.available_balance)
                else:
                    balance = 0
                    
                balance += get_external_balance(coins_dict, currency)
                if currency in withdrawn_balances: # withdrawn_balances should use uppercase keys if coins_dict does
                    balance += withdrawn_balances[currency]
                balances[currency] = balance * prices.get(currency, 0) # Use .get for safety if price missing
    
    # Ensure all configured coins have an entry, even if 0
    for c_symbol in coins_dict.keys():
        if c_symbol not in balances:
            balances[c_symbol] = get_external_balance(coins_dict, c_symbol) * prices.get(c_symbol, 0)
        if args.fiat_currency not in balances: # Ensure fiat currency is initialized
            balances[args.fiat_currency] = 0.0
            
    return balances

def get_account_by_currency(accounts_response, currency_symbol):
    if accounts_response and accounts_response.accounts:
        for acc in accounts_response.accounts:
            if acc.currency == currency_symbol:
                return acc
    return None


def set_buy_order(args, coin_symbol, price, size, client, db_session):
    product_id = f"{coin_symbol}-{args.fiat_currency}"
    # Use coin-specific precision for size and price
    size_precision = get_decimal_precision(coin_symbol)
    price_precision = get_price_precision(coin_symbol)
    
    formatted_price = str(Decimal(str(price)).quantize(price_precision, rounding=ROUND_DOWN))
    formatted_size = str(Decimal(str(size)).quantize(size_precision, rounding=ROUND_DOWN))

    print(f"Placing limit buy order: coin={coin_symbol}, price={formatted_price}, size={formatted_size}")
    
    # client_order_id should be unique. SDK generates one if not provided or empty.
    # The old script didn't provide one here, relying on the exchange.
    # The new SDK's helpers generate one.
    # limit_order_gtc takes client_order_id, let's pass an empty string to let SDK handle it.
    try:
        order_response = client.limit_order_gtc(
            client_order_id="", # Let SDK generate
            product_id=product_id,
            side="BUY",
            base_size=formatted_size, # size is base_size
            limit_price=formatted_price,
            post_only=True
        )
        print(f"Order response: {json.dumps(order_response.to_dict(), indent=2)}")

        # Handle both object and dictionary response structures
        if isinstance(order_response, dict):
            success = order_response.get('success', False)
            success_response = order_response.get('success_response', {})
            order_id = success_response.get('order_id')
        else:
            success = getattr(order_response, 'success', False)
            success_response = getattr(order_response, 'success_response', None)
            if success_response:
                if isinstance(success_response, dict):
                    order_id = success_response.get('order_id')
                else:
                    order_id = getattr(success_response, 'order_id', None)
            else:
                order_id = None

        if success and order_id:
            db_session.add(
                Order(
                    currency=coin_symbol,
                    size=float(size), # Store as float
                    price=float(price), # Store as float
                    cbpro_order_id=order_id, # Fixed field name
                    created_at=datetime.now(timezone.utc), # Using current UTC time
                )
            )
            db_session.commit()
            return order_response
        else:
            print(f"Order placement failed or no success response: {order_response}")
            return order_response # Or handle error appropriately
    except HTTPError as e:
        print(f"HTTPError placing order for {product_id}: {e}")
        raise
    except Exception as e:
        print(f"Error placing order for {product_id}: {e}")
        raise


def generate_buy_orders(coins_config, coin_symbol, args, amount_to_buy_fiat, current_price):
    getcontext().prec = 8 # Precision for crypto size calculations
    
    buy_orders = []
    
    minimum_order_value_fiat = coins_config[coin_symbol].get("minimum_order_size", 0.01) # This is quote_min_size

    # Ensure amount_to_buy_fiat meets the minimum order value
    if amount_to_buy_fiat < minimum_order_value_fiat:
        print(f"Amount to buy {amount_to_buy_fiat} for {coin_symbol} is less than minimum order value {minimum_order_value_fiat}. Skipping.")
        return buy_orders

    # Calculate number of orders
    # Ensure each split order also meets minimum value
    # max number of orders if each is minimum_order_value_fiat
    max_possible_orders_by_value = math.floor(amount_to_buy_fiat / minimum_order_value_fiat)
    
    number_of_orders = min(
        args.order_count,
        max(1, max_possible_orders_by_value) 
    )
    
    if number_of_orders == 0 : # Should be caught by amount_to_buy_fiat check already
        return buy_orders

    # Amount of fiat per order
    amount_fiat_per_order = Decimal(str(amount_to_buy_fiat)) / Decimal(str(number_of_orders))
    print(f"precision: {get_decimal_precision(coin_symbol)}")
    amount_fiat_per_order = amount_fiat_per_order.quantize(get_decimal_precision(coin_symbol), rounding=ROUND_DOWN)
    print(f"Initial amount fiat per order: {amount_fiat_per_order}")

    if amount_fiat_per_order < Decimal(str(minimum_order_value_fiat)):
        # This can happen if amount_to_buy_fiat is small, and order_count is high
        # Recalculate number_of_orders based on minimum value per order
        number_of_orders = max(1, math.floor(Decimal(str(amount_to_buy_fiat)) / Decimal(str(minimum_order_value_fiat))))
        print(f"Recalculated number of orders: {number_of_orders}")
        amount_fiat_per_order = Decimal(str(amount_to_buy_fiat)) / Decimal(str(number_of_orders))
        amount_fiat_per_order = amount_fiat_per_order.quantize(get_decimal_precision(coin_symbol), rounding=ROUND_DOWN)
        print(f"Adjusted amount fiat per order: {amount_fiat_per_order}")

    discount_factor = Decimal(str(1 - args.starting_discount))
    price_decimal = Decimal(str(current_price))
    print(f"Starting discount factor: {discount_factor}, price: {price_decimal}")

    for i in range(number_of_orders):
        # Ensure discounted price has appropriate precision
        
        discounted_price = (price_decimal * discount_factor).quantize(get_price_precision(coin_symbol), rounding=ROUND_DOWN)
        print(f"Calculated discounted price: {discounted_price} for {coin_symbol} (original: {price_decimal}, discount: {discount_factor}, precision: {get_price_precision(coin_symbol)})")
        print(f"Discounted price for {coin_symbol}: {discounted_price}")
        if discounted_price <= Decimal("0"): # Price cannot be zero or negative
            print(f"Warning: Discounted price for {coin_symbol} is too low ({discounted_price}). Skipping this order split.")
            continue
            
        # Calculate size in base currency - as price increases, size should decrease
        # to maintain the same fiat value per order
        print(f"Amount fiat per order for {coin_symbol}: {amount_fiat_per_order}")
        print(f"Discounted price for {coin_symbol}: {discounted_price}")
        size_base_currency = amount_fiat_per_order / discounted_price
        size_base_currency = size_base_currency.quantize(get_decimal_precision(coin_symbol), rounding=ROUND_DOWN)

        if size_base_currency * discounted_price < Decimal(str(minimum_order_value_fiat)):
             print(f"Skipping order for {coin_symbol} at price {discounted_price} due to size {size_base_currency} valuing less than minimum.")
             continue

        buy_orders.append({"price": float(discounted_price), "size": float(size_base_currency)})
        discount_factor -= Decimal(str(args.discount_step))
        
    return buy_orders


def place_buy_orders(args, amount_to_buy_fiat, coins_config, coin_symbol, current_price, client, db_session):
    if amount_to_buy_fiat <= 0.01: # Miniscule amount
        print(
            f"{coin_symbol}: amount_to_buy_fiat={amount_to_buy_fiat}, not buying {coin_symbol}"
        )
        return
    if current_price <= 0:
        print(f"Current price={current_price} for {coin_symbol}, not buying.")
        return
    print(f"Placing buy orders for {coin_symbol} with amount {amount_to_buy_fiat} at price {current_price}")
    buy_orders_params = generate_buy_orders(coins_config, coin_symbol, args, amount_to_buy_fiat, current_price)
    for order_params in buy_orders_params:
        set_buy_order(
            args, coin_symbol, order_params["price"], order_params["size"], client, db_session
        )


def start_buy_orders(
    args, coins_config, accounts_response, prices, fiat_balances_per_coin, total_fiat_to_spend, client, db_session
):
    # coins_config: original dict from args.coins, updated with min_order_size
    # fiat_balances_per_coin: dict of coin_symbol -> fiat_value_of_coin_holding
    # total_fiat_to_spend: fiat amount available for buying (after fees reserved)
    
    coin_symbols_list = list(coins_config.keys())
    weights = get_weights(coin_symbols_list, args.fiat_currency)

    # Total portfolio value in fiat (sum of current holdings in fiat + fiat to spend now)
    current_portfolio_fiat_value = sum(fiat_balances_per_coin.values()) + total_fiat_to_spend
    print(f"Current total portfolio value (including cash to spend): {current_portfolio_fiat_value:.2f} {args.fiat_currency}")

    target_fiat_value_per_coin = {}
    for c_symbol in coin_symbols_list:
        target_fiat_value_per_coin[c_symbol.upper()] = current_portfolio_fiat_value * weights.get(c_symbol.upper(), 0)
    
    print(f"Target fiat value per coin: {json.dumps(target_fiat_value_per_coin, indent=2)}")

    fiat_to_allocate_per_coin = {}
    current_sum_of_positive_allocations = 0
    for c_symbol in coin_symbols_list:
        # Difference needed to reach target allocation for this coin
        diff = target_fiat_value_per_coin[c_symbol.upper()] - fiat_balances_per_coin.get(c_symbol.upper(), 0)
        if diff > 0:
            fiat_to_allocate_per_coin[c_symbol.upper()] = diff
            current_sum_of_positive_allocations += diff
        else:
            fiat_to_allocate_per_coin[c_symbol.upper()] = 0 # No need to buy if already at or above target

    print(f"Ideal fiat allocation to buy per coin (before normalization): {json.dumps(fiat_to_allocate_per_coin, indent=2)}")

    # Normalize these ideal allocations based on the actual total_fiat_to_spend
    final_fiat_to_buy_per_coin = {}
    if current_sum_of_positive_allocations > 0:
        for c_symbol in coin_symbols_list:
            normalized_amount = (fiat_to_allocate_per_coin[c_symbol.upper()] / current_sum_of_positive_allocations) * total_fiat_to_spend
            final_fiat_to_buy_per_coin[c_symbol.upper()] = math.floor(normalized_amount * 100) / 100.0 # Floor to 2 decimal places
    else: # This case means no coin needs buying to reach target proportions, or only selling would be needed.
          # Distribute total_fiat_to_spend according to target weights directly if all diffs were <= 0.
        print("No specific coin needs buying to rebalance towards target. Distributing available fiat according to weights.")
        for c_symbol in coin_symbols_list:
            final_fiat_to_buy_per_coin[c_symbol.upper()] = math.floor((total_fiat_to_spend * weights.get(c_symbol.upper(),0)) * 100) / 100.0


    print(f"Final fiat amount to spend per coin: {json.dumps(final_fiat_to_buy_per_coin, indent=2)}")

    for c_symbol in coin_symbols_list:
        if c_symbol.upper() in prices and prices[c_symbol.upper()] > 0:
            place_buy_orders(
                args, final_fiat_to_buy_per_coin[c_symbol.upper()], coins_config, c_symbol.upper(), prices[c_symbol.upper()], client, db_session
            )
        else:
            print(f"Skipping buy for {c_symbol} due to missing or invalid price.")


def execute_withdrawal(client, amount_str, currency_symbol, crypto_address, db_session):
    # Ensure amount is a string with correct precision for the API
    try:
        amount_decimal = Decimal(str(amount_str))
        formatted_amount = str(amount_decimal.quantize(get_decimal_precision(currency_symbol), rounding=ROUND_DOWN))
    except:
        print(f"Could not format amount {amount_str} for withdrawal. Using as is.")
        formatted_amount = str(amount_str)

    print(f"Attempting to withdraw {formatted_amount} {currency_symbol} to {crypto_address}")

    # NOTE: The coinbase-advanced-py SDK version reflected in the provided files
    # does not show a direct method in RESTClient for crypto withdrawals.
    # This functionality might be available through a different API,
    # via the Coinbase website/app, or a future/different version of the SDK.
    # The original script's client.withdraw_to_crypto(...) call cannot be directly translated.
    print("Crypto withdrawal functionality is not directly available in this SDK version.")
    print("Please handle withdrawals manually or explore other Coinbase APIs/SDKs for this feature.")

    transaction_response_simulated = {
        # "id": "simulated_withdrawal_id_456"
    } # Example

    if "id" in transaction_response_simulated: # This block will not run with the current placeholder
        # db_session.add(
        #     Withdrawal(
        #         amount=float(formatted_amount),
        #         currency=currency_symbol,
        #         crypto_address=crypto_address,
        #         coinbase_withdrawal_id=transaction_response_simulated["id"], # Renamed field
        #         # timestamp might be useful here too: withdrawn_at=datetime.now(timezone.utc)
        #     )
        # )
        # db_session.commit()
        pass


def withdraw(coins_config, accounts_response, client, db_session):
    if not (accounts_response and accounts_response.accounts):
        print("No accounts data to process for withdrawals.")
        return

    for coin_symbol, config in coins_config.items():
        withdrawal_address = config.get("withdrawal_address")
        if not withdrawal_address:
            print(f"No withdrawal address specified for {coin_symbol}, not withdrawing.")
            continue

        account = get_account_by_currency(accounts_response, coin_symbol)
        if not account:
            print(f"No account found for {coin_symbol}, cannot withdraw.")
            continue
        
        balance_to_withdraw = float(account.available_balance.value)

        # Consider a minimum withdrawal amount if applicable from API docs or typical exchange behavior
        if balance_to_withdraw < 0.00000001: # Example small threshold
            print(
                f"{coin_symbol} balance {balance_to_withdraw} is too small, not withdrawing."
            )
        else:
            execute_withdrawal(
                client,
                str(balance_to_withdraw), # Pass as string
                coin_symbol,
                withdrawal_address,
                db_session,
            )


def get_withdrawn_balances(db_session):
    from sqlalchemy import func # Keep this import local if only used here

    withdrawn_balances = {}
    try:
        # Ensure Withdrawal.amount is a numeric type in the DB for sum() to work correctly.
        withdrawals = (
            db_session.query(func.sum(Withdrawal.amount), Withdrawal.currency)
            .group_by(Withdrawal.currency)
            .all()
        )
        for total_amount, currency_symbol in withdrawals:
            withdrawn_balances[currency_symbol.upper()] = total_amount if total_amount else 0.0
    except Exception as e:
        print(f"Error fetching withdrawn balances from DB: {e}")
        # Return empty or partially filled dict, or raise
    return withdrawn_balances


def buy(args, coins_config, client, db_session):
    # coins_config is the original dict from args.coins
    print("Starting buy and (maybe) withdrawal process.")
    
    print("Step 1: Cancelling existing open orders for configured products.")
    active_product_ids_to_cancel = [f"{coin_symbol.upper()}-{args.fiat_currency.upper()}" for coin_symbol in coins_config.keys()]
    
    try:
        for product_id in active_product_ids_to_cancel:
            print(f"Fetching open orders for {product_id} to cancel...")
            # Consider relevant statuses for cancellation
            open_orders_response = client.list_orders(product_ids=[product_id], order_status=["OPEN", "PENDING"])
            if open_orders_response.orders:
                order_ids_to_cancel = [o.order_id for o in open_orders_response.orders]
                if order_ids_to_cancel:
                    print(f"Cancelling order IDs for {product_id}: {order_ids_to_cancel}")
                    cancel_response = client.cancel_orders(order_ids=order_ids_to_cancel)
                    # Process cancel_response to check for success/failures
                    if cancel_response.results:
                        for res in cancel_response.results:
                            if res.success:
                                print(f"Successfully cancelled order {res.order_id}")
                            else:
                                print(f"Failed to cancel order {res.order_id}: {res.failure_reason}")
                else:
                    print(f"No open orders found for {product_id} to cancel.")
            else:
                print(f"No orders listed for {product_id} (or error in listing).")
    except HTTPError as e:
        print(f"HTTPError during order cancellation pre-process: {e}") # Continue if non-critical
    except Exception as e:
        print(f"Error during order cancellation pre-process: {e}") # Continue if non-critical


    print("\nStep 2: Fetching current account balances and market prices.")
    try:
        accounts_response = client.get_accounts()
        # Update coins_config with minimum order sizes from product info
        coins_config_updated = get_products_info(client, coins_config.copy(), args.fiat_currency.upper())
        
        coin_symbols_list = list(coins_config_updated.keys())
        prices = get_prices(client, coin_symbols_list, args.fiat_currency.upper())
    except Exception as e:
        print(f"Critical error fetching accounts/products/prices: {e}. Aborting buy cycle.")
        return

    withdrawn_balances = get_withdrawn_balances(db_session)
    
    print(f"Accounts: {json.dumps(accounts_response.to_dict(), indent=2) if accounts_response else 'N/A'}")
    print(f"Prices: {json.dumps(prices, indent=2)}")
    print(f"Coins Config (with min sizes): {json.dumps(coins_config_updated, indent=2)}")
    print(f"Withdrawn Balances from DB: {json.dumps(withdrawn_balances, indent=2)}")

    fiat_balances_per_coin = get_fiat_balances(args, coins_config_updated, accounts_response, withdrawn_balances, prices)
    print(f"Current Fiat Value of Holdings (per coin): {json.dumps(fiat_balances_per_coin, indent=2)}")

    available_fiat_cash = fiat_balances_per_coin.get(args.fiat_currency.upper(), 0.0)
    print(f"Available Fiat Cash ({args.fiat_currency.upper()}): {available_fiat_cash:.2f}")

    # Reserve fee amount from available fiat cash
    fee_amount = args.base_fee * available_fiat_cash
    print(f"Reserving {fee_amount:.2f} {args.fiat_currency.upper()} for fees (base_fee_rate={args.base_fee})")
    fiat_to_spend_after_fees = available_fiat_cash - fee_amount

    if fiat_to_spend_after_fees > args.withdrawal_threshold: # Renamed from withdrawal_amount for clarity
        print(
            f"Fiat balance after fee reservation ({fiat_to_spend_after_fees:.2f} {args.fiat_currency.upper()}) is above threshold ({args.withdrawal_threshold} {args.fiat_currency.upper()}). Proceeding with buys."
        )
        start_buy_orders(
            args,
            coins_config_updated,
            accounts_response, # Pass this to avoid re-fetching
            prices,
            fiat_balances_per_coin, # Pass current holdings value
            fiat_to_spend_after_fees, # Pass the actual amount to spend
            client,
            db_session,
        )
    else:
        print(
            f"Fiat balance after fee reservation ({fiat_to_spend_after_fees:.2f} {args.fiat_currency.upper()}) is not above threshold ({args.withdrawal_threshold} {args.fiat_currency.upper()})."
            " Proceeding to withdraw coins without new buys."
        )
        # Fetch accounts again if needed, or pass if still valid
        # The current accounts_response should be fresh enough
        withdraw(coins_config_updated, accounts_response, client, db_session)


def main():
    default_coins_str = """
    {
      "BTC":{
        "name":"Bitcoin",
        "withdrawal_address":null,
        "external_balance":0
      },
      "ETH":{
        "name":"Ethereum",
        "withdrawal_address":null,
        "external_balance":0
      },
      "LTC":{
        "name":"Litecoin",
        "withdrawal_address":null,
        "external_balance":0
      }
    }
    """

    parser = argparse.ArgumentParser(
        description="Coinbase Advanced Trade Bot: Buy coins based on market cap weights or deposit funds.",
        epilog=f"Default coins configuration: {default_coins_str}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=['deposit', 'buy'], help="Operational mode: 'deposit' or 'buy'", required=True)
    parser.add_argument("--amount", type=float, help="Amount for deposit (only in 'deposit' mode)")
    parser.add_argument("--key", help="Coinbase API Key (name, e.g., organizations/org-id/apiKeys/key-id)", required=True)
    parser.add_argument("--secret", help="Coinbase API Secret (the private key string)", required=True)
    # Passphrase is not used with CDP API keys for Advanced Trade
    # parser.add_argument("--passphrase", help="API passphrase", required=True) 
    # API URL is handled by the SDK, using its default or allowing base_url override if necessary,
    # but for typical use, it's not needed.
    # parser.add_argument("--api-url", help="API URL", default="https://api.coinbase.com")

    parser.add_argument("--payment-method-id", help="Payment Method ID for fiat deposits (only in 'deposit' mode)")
    parser.add_argument("--starting-discount", type=float, help="Starting discount for limit buy orders (e.g., 0.005 for 0.5%%, default: 0.005)", default=0.005)
    parser.add_argument("--discount-step", type=float, help="Incremental discount step for subsequent buy orders (e.g., 0.01 for 1%%, default: 0.01)", default=0.01)
    parser.add_argument("--order-count", type=int, help="Number of buy orders to split into (default: 5)", default=5)
    parser.add_argument("--fiat-currency", help="Fiat currency for trading and balances (default: USD)", default="USD")
    parser.add_argument("--withdrawal-threshold", help="If fiat balance (after reserving fees) is below this, withdraw instead of buying (default: 25.0)", type=float, default=25.0)
    parser.add_argument("--db-engine", help="SQLAlchemy DB engine string (default: sqlite:///cbpro_history.db)", default="sqlite:///cbpro_history.db")
    parser.add_argument("--max-retries", help="Max retries on API failures (default: 3)", type=int, default=3)
    parser.add_argument("--coins", help="JSON string for coins to trade, their names, withdrawal addresses, and external balances.", default=default_coins_str)
    parser.add_argument("--base-fee", help="Estimated trading fee rate to reserve from fiat balance (e.g., 0.006 for 0.6%%, default: 0.0060)", type=float, default=0.0060) # Typical taker fee

    args = parser.parse_args()
    
    try:
        coins_config = json.loads(args.coins)
        # Ensure coin symbols are uppercase for consistency
        coins_config = {k.upper(): v for k,v in coins_config.items()}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON string for --coins argument: {e}")
        sys.exit(1)
        
    print(f"--coins='{json.dumps(coins_config, separators=(',', ':'))}'")
    print(f"Using API Key: {args.key[:25]}...") # Print only a part of the key for security

    client = RESTClient(api_key=args.key, api_secret=args.secret)
    db_session = get_session(args.db_engine)

    retry_count = 0
    backoff_seconds = 5
    while retry_count < args.max_retries:
        retry_count += 1
        print(f"Attempt {retry_count} of {args.max_retries}")
        try:
            if args.mode == "deposit":
                deposit(args, client, db_session)
            elif args.mode == "buy":
                buy(args, coins_config, client, db_session)
            sys.stdout.flush()
            # If successful, exit
            sys.exit(0) 
        except Exception as e:
            print(f"Caught an exception: {e}")
            import traceback
            traceback.print_exc()
            sys.stderr.flush()
            sys.stdout.flush()
            if retry_count < args.max_retries:
                print(f"Sleeping for {backoff_seconds}s before retrying...")
                time.sleep(backoff_seconds)
                backoff_seconds *= 2 # Exponential backoff
            else:
                print("Max retries reached. Exiting.")
                sys.exit(1)

if __name__ == "__main__": # Corrected conditional
    main()