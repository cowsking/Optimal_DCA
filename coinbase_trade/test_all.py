#!/usr/bin/env python3

from coinbase.rest import RESTClient
import argparse
import sys
import math
import time
import dateutil.parser
import json
import requests
from .history import Order, Deposit, Withdrawal, get_session
from requests.exceptions import HTTPError


def get_weights(coins, fiat_currency):
    market_cap = {}
    try:
        response = requests.get("https://api.coincap.io/v2/assets")
        assets = response.json()
        coin_data = {}
        for coin in assets["data"]:
            coin_data[coin["symbol"]] = coin
        for c in coins:
            market_cap[c] = float(coin_data[c]["marketCapUsd"])
    except HTTPError as e:
        print(
            "caught exception when fetching ticker for {} with name={}".format(
                c, coins[c]["name"]
            )
        )
        raise e

    total_market_cap = sum(market_cap.values())

    weights = {}
    for c in coins:
        weights[c] = market_cap[c] / total_market_cap
    print("coin weights:")
    for w in weights:
        print("  {0}: {1:.4f}".format(w, weights[w]))
    print()
    return weights


def deposit(args, client, db_session):
    if args.amount is None:
        print("please specify deposit amount with `--amount`")
        sys.exit(1)
    if args.payment_method_id is None:
        print("please provide a bank ID with `--payment-method-id`")
        sys.exit(1)
    print("performing deposit, amount={} {}".format(args.amount, args.fiat_currency))
    deposit = client.deposit(
        payment_method_id=args.payment_method_id,
        amount=args.amount,
        currency=args.fiat_currency,
    )
    print("deposit={}".format(deposit))
    if "id" in deposit:
        db_session.add(
            Deposit(
                payment_method_id=args.payment_method_id,
                amount=args.amount,
                currency=args.fiat_currency,
                payout_at=dateutil.parser.parse(deposit["payout_at"]),
                cbpro_deposit_id=deposit["id"],
            )
        )
        db_session.commit()


def get_products(client, coins, fiat_currency):
    products = client.list_products()
    for p in products:
        if p["base_currency"] in coins and p["quote_currency"] == fiat_currency:
            coins[p["base_currency"]]["minimum_order_size"] = float(p["min_market_funds"])
    return products


def get_prices(client, coins, fiat_currency):
    prices = {}
    for c in coins:
        ticker = client.get_product_ticker(
            product_id="{}-{}".format(c, fiat_currency)
        )
        if "price" not in ticker:
            raise (Exception("no price available for {} ticker={}".format(c, ticker)))
        print("{} ticker={}".format(c, ticker))
        prices[c] = float(ticker["price"])
    return prices


def get_external_balance(coins, coin):
    external_balance = float(coins[coin].get("external_balance", 0))
    if external_balance > 0:
        print("including external balance of {} {}".format(external_balance, coin))
    return external_balance


def get_fiat_balances(args, coins, accounts, withdrawn_balances, prices):
    balances = {}
    for a in accounts:
        if a["currency"] == args.fiat_currency:
            balances[args.fiat_currency] = float(a["balance"])
        elif a["currency"] in coins:
            balance = float(a["balance"]) + get_external_balance(coins, a["currency"])
            if a["currency"] in withdrawn_balances:
                balance = balance + withdrawn_balances[a["currency"]]
            balances[a["currency"]] = balance * prices[a["currency"]]
    for c in coins:
        if c not in balances:
            balances[c] = 0
    return balances


def get_account(accounts, currency):
    for a in accounts:
        if a["currency"] == currency:
            return a


def set_buy_order(args, coin, price, size, client, db_session):
    print("placing order coin={0} price={1:.2f} size={2:.8f}".format(coin, price, size))
    order = client.create_limit_order(
        product_id="{}-{}".format(coin, args.fiat_currency),
        side="BUY",
        price="{0:.2f}".format(price),
        size="{0:.8f}".format(size),
        post_only=True
    )
    print("order={}".format(order))
    if "id" in order:
        db_session.add(
            Order(
                currency=coin,
                size=size,
                price=price,
                cbpro_order_id=order["id"],
                created_at=dateutil.parser.parse(order["created_at"]),
            )
        )
        db_session.commit()
    return order


def generate_buy_orders(coins, coin, args, amount_to_buy, price):
    from decimal import Decimal, getcontext, ROUND_DOWN

    getcontext().prec = 8
    getcontext().rounding = ROUND_DOWN
    buy_orders = []

    # If the size is <= minimum * 5, set a single buy order, because otherwise
    # it will get rejected
    minimum_order_size = coins[coin].get("minimum_order_size", 0.01)
    number_of_orders = min(
        [
            args.order_count,
            max([1, math.floor(amount_to_buy / (minimum_order_size * price))]),
        ]
    )

    # Set 5 buy orders
    amount = Decimal(math.floor(100 * amount_to_buy / number_of_orders)) / Decimal(100)
    discount = 1 - args.starting_discount

    for _ in range(0, number_of_orders):
        discounted_price = Decimal(math.floor(100.0 * price * discount)) / Decimal(100)
        size = amount / discounted_price

        buy_orders.append({"price": float(discounted_price), "size": float(size)})
        discount = discount - args.discount_step
    return buy_orders


def place_buy_orders(args, amount_to_buy, coins, coin, price, client, db_session):
    if amount_to_buy <= 0.01:
        print(
            "{}: balance_difference_fiat={}, not buying {}".format(
                coin, amount_to_buy, coin
            )
        )
        return
    if price <= 0:
        print("price={}, not buying {}".format(price, coin))
        return

    buy_orders = generate_buy_orders(coins, coin, args, amount_to_buy, price)
    for order in buy_orders:
        set_buy_order(
            args, coin, order["price"], order["size"], client, db_session
        )


def start_buy_orders(
    args, coins, accounts, prices, fiat_balances, fiat_amount, client, db_session
):
    weights = get_weights(coins, args.fiat_currency)

    # Determine amount of each coin, in fiat, to buy
    fiat_balance_sum = sum(fiat_balances.values())
    print("fiat_balance_sum={}".format(fiat_balance_sum))

    target_amount_fiat = {}
    for c in coins:
        target_amount_fiat[c] = fiat_balance_sum * weights[c]
    print("target_amount_fiat={}".format(target_amount_fiat))

    balance_differences_fiat = {}
    for c in coins:
        balance_differences_fiat[c] = round(target_amount_fiat[c] - fiat_balances[c], 2)
    print("balance_differences_fiat={}".format(balance_differences_fiat))

    # Calculate portion of each to buy
    sum_to_buy = 0
    for coin in balance_differences_fiat:
        if balance_differences_fiat[coin] >= 0:
            sum_to_buy += balance_differences_fiat[coin]
    amount_to_buy = {}
    for coin in balance_differences_fiat:
        amount_to_buy[coin] = (
            math.floor(
                100 * (balance_differences_fiat[coin] / sum_to_buy) * fiat_amount
            )
            / 100.0
        )

    print("amount_to_buy={}".format(amount_to_buy))

    for c in coins:
        place_buy_orders(
            args, amount_to_buy[c], coins, c, prices[c], client, db_session
        )


def execute_withdrawal(client, amount, currency, crypto_address, db_session):
    # The API does something goofy where the account balance
    # has more decimal places than the withdrawal API supports, so
    # we have to account for that here. Plus, the format()
    # function will round the float, so we have to do some
    # janky flooring.
    amount = "{0:.9f}".format(float(amount))[0:-1]
    print("withdrawing {} {} to {}".format(amount, currency, crypto_address))
    transaction = client.withdraw_to_crypto(
        amount=amount, currency=currency, crypto_address=crypto_address
    )
    print("transaction={}".format(transaction))
    if "id" in transaction:
        db_session.add(
            Withdrawal(
                amount=amount,
                currency=currency,
                crypto_address=crypto_address,
                cbpro_withdrawal_id=transaction["id"],
            )
        )
        db_session.commit()


def withdraw(coins, accounts, client, db_session):
    for coin in coins:
        if (
            "withdrawal_address" not in coins[coin]
            or coins[coin]["withdrawal_address"] is None
            or len(coins[coin]["withdrawal_address"]) < 1
        ):
            print("no {} withdraw address specified, " "not withdrawing".format(coin))
            continue
        account = get_account(accounts, coin)
        if float(account["balance"]) < 0.01:
            print(
                "{} balance only {}, not withdrawing".format(coin, account["balance"])
            )
        else:
            execute_withdrawal(
                client,
                account["balance"],
                coin,
                coins[coin]["withdrawal_address"],
                db_session,
            )


def get_withdrawn_balances(db_session):
    from sqlalchemy import func

    withdrawn_balances = {}
    withdrawals = (
        db_session.query(func.sum(Withdrawal.amount), Withdrawal.currency)
        .group_by(Withdrawal.currency)
        .all()
    )
    for w in withdrawals:
        withdrawn_balances[w[1]] = w[0]
    return withdrawn_balances


def buy(args, coins, client, db_session):
    print("starting buy and (maybe) withdrawal")
    print("first, cancelling orders")
    products = get_products(client, coins, args.fiat_currency)
    print("products={}".format(products))
    for c in coins:
        client.cancel_orders(product_id="{}-{}".format(c, args.fiat_currency))
    # Check if there's any fiat available to execute a buy
    accounts = client.list_accounts()
    prices = get_prices(client, coins, args.fiat_currency)
    withdrawn_balances = get_withdrawn_balances(db_session)
    print("accounts={}".format(accounts))
    print("prices={}".format(prices))
    print("withdrawn_balances={}".format(withdrawn_balances))

    fiat_balances = get_fiat_balances(args, coins, accounts, withdrawn_balances, prices)
    print("fiat_balances={}".format(fiat_balances))

    fiat_amount = fiat_balances[args.fiat_currency]
    fee_amount = args.base_fee * fiat_amount
    print("reserving {} for fees, base_fee={}".format(fee_amount, args.base_fee))
    fiat_amount -= fee_amount

    if fiat_amount > args.withdrawal_amount:
        print(
            "fiat balance above {} {}, buying more".format(
                args.withdrawal_amount, args.fiat_currency
            )
        )
        start_buy_orders(
            args,
            coins,
            accounts,
            prices,
            fiat_balances,
            fiat_amount,
            client,
            db_session,
        )
    else:
        print(
            "only {} {} fiat balance remaining, withdrawing"
            " coins without buying".format(fiat_amount, args.fiat_currency)
        )
        withdraw(coins, accounts, client, db_session)


def main():
    default_coins = """
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
        description="Buy coins!",
        epilog="Default coins are as follows: {}".format(default_coins),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", help="mode (deposit or buy)", required=True)
    parser.add_argument("--amount", type=float, help="amount to deposit")
    parser.add_argument("--key", help="API key", required=True)
    parser.add_argument("--b64secret", help="API secret", required=True)
    parser.add_argument("--passphrase", help="API passphrase", required=True)
    parser.add_argument(
        "--api-url",
        help="API URL (default: https://api.pro.coinbase.com)",
        default="https://api.pro.coinbase.com",
    )
    parser.add_argument(
        "--payment-method-id", help="Payment method ID for fiat deposits"
    )
    parser.add_argument(
        "--starting-discount",
        type=float,
        help="starting discount (default: 0.005)",
        default=0.005,
    )
    parser.add_argument(
        "--discount-step",
        type=float,
        help="discount step between orders (default: 0.01)",
        default=0.01,
    )
    parser.add_argument(
        "--order-count", type=int, help="number of orders (default: 5)", default=5
    )
    parser.add_argument(
        "--fiat-currency", help="Fiat currency (default: USD)", default="USD"
    )
    parser.add_argument(
        "--withdrawal-amount",
        help="withdraw when fiat " "balance drops below this amount (default: 25)",
        type=float,
        default=25,
    )
    parser.add_argument(
        "--db-engine",
        help="SQLAlchemy DB engine " "(default: sqlite:///cbpro_history.db)",
        default="sqlite:///cbpro_history.db",
    )
    parser.add_argument(
        "--max-retries",
        help="Maximum number of times to "
        "retry if there are any failures, such as API issues "
        "(default: 3)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--coins",
        help="Coins to trade, minimum trade size,"
        " withdrawal addresses and external balances. "
        "Accepts a JSON string.",
        default=default_coins,
    )
    parser.add_argument(
        "--base-fee",
        help="Default base fee to subtract " "from overall balance.",
        type=float,
        default=0.0015,
    )

    args = parser.parse_args()
    coins = json.loads(args.coins)
    print("--coins='{}'".format(json.dumps(coins, separators=(",", ":"))))

    client = RESTClient(api_key=args.key, api_secret=args.b64secret)
    db_session = get_session(args.db_engine)

    retry = 0
    backoff = 5
    while retry < args.max_retries:
        retry += 1
        print("attempt {} of {}".format(retry, args.max_retries))
        try:
            if args.mode == "deposit":
                deposit(args, client, db_session)
            elif args.mode == "buy":
                buy(args, coins, client, db_session)
            sys.stdout.flush()
            sys.exit(0)
        except Exception as e:
            print("caught an exception: ", e)
            import traceback

            traceback.print_exc()
            sys.stderr.flush()
            sys.stdout.flush()
            print("sleeping for {}s".format(backoff))
            time.sleep(backoff)
            backoff = backoff * 2


if __name__ == "main":
    main()
