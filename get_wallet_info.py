import requests
import json
import time
import datetime
import cryptocompare

# Set your Alchemy Solana endpoint
RPC_ENDPOINT = "https://solana-mainnet.g.alchemy.com/v2/JL7Nvs-hqR1JtHzHl1batar9ICzI38UX"  # e.g. "https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

headers = {"Content-Type": "application/json"}

def solana_rpc_request(method, params):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    resp = requests.post(RPC_ENDPOINT, json=payload, headers=headers)
    return resp.json()

def get_signatures_for_address(pubkey, limit=10):
    data = solana_rpc_request("getSignaturesForAddress", [pubkey, {"limit": limit}])
    return data.get("result", [])

def get_transaction(signature):
    # Include maxSupportedTransactionVersion to handle newer transactions
    data = solana_rpc_request("getTransaction", [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}])
    return data

def get_token_price_at_time(symbol, dt):
    """
    Fetch historical price for the given symbol at time dt using cryptocompare.
    symbol: e.g., "SOL"
    dt: a datetime object (in UTC)
    """
    timestamp = int(dt.timestamp())
    price_data = cryptocompare.get_historical_price(symbol, 'USD', timestamp=timestamp)
    if price_data and symbol in price_data:
        return price_data[symbol].get('USD')
    return None

def process_transactions(pubkey, limit=10):
    sigs = get_signatures_for_address(pubkey, limit=limit)
    trades = []  # Will store (time, symbol, amount, side, price)

    symbol = "SOL"
    for entry in sigs:
        signature = entry["signature"]
        tx_data = get_transaction(signature)

        if "error" in tx_data:
            # Handle rate limits or errors
            if tx_data["error"]["code"] == 429:
                print("Rate limited. Waiting before retry...")
                time.sleep(2)
                tx_data = get_transaction(signature)
            else:
                continue

        result = tx_data.get("result", {})
        meta = result.get("meta", {})
        if not meta:
            continue

        blockTime = result.get("blockTime")
        if blockTime is None:
            continue
        tx_time = datetime.datetime.fromtimestamp(blockTime, datetime.timezone.utc)

        preBalances = meta.get("preBalances", [])
        postBalances = meta.get("postBalances", [])

        # Assume the first account (index 0) is the user's main SOL account
        # This is a simplification; in practice, you'd identify which account belongs to the user.
        if len(preBalances) == 0 or len(postBalances) == 0:
            continue

        pre_sol = preBalances[0] / 1e9  # Convert lamports to SOL
        post_sol = postBalances[0] / 1e9
        change = post_sol - pre_sol

        if change == 0:
            # No SOL change, skip
            continue

        price = get_token_price_at_time(symbol, tx_time)
        if not price:
            # If we can't get price, skip this trade
            continue

        if change > 0:
            # Received SOL -> treat as buy
            trades.append((tx_time, symbol, change, "buy", price))
        else:
            # Lost SOL -> treat as sell
            trades.append((tx_time, symbol, abs(change), "sell", price))

        # Sleep briefly to avoid rate limits
        time.sleep(0.5)

    return trades

def compute_pnl_and_future_analysis(trades):
    # FIFO cost-basis
    inventory = {}
    total_pnl = 0.0
    symbol = "SOL"

    # Sort trades by time just in case
    trades.sort(key=lambda x: x[0])

    for t_time, s, amount, side, price in trades:
        if side == "buy":
            if s not in inventory:
                inventory[s] = []
            inventory[s].append((t_time, amount, price))
        elif side == "sell":
            if s not in inventory or not inventory[s]:
                # Selling something not bought before? Skip
                continue
            # Match against buys in FIFO manner
            remaining = amount
            pnl_for_this_sell = 0.0

            while remaining > 0 and inventory[s]:
                buy_time, buy_amt, buy_price = inventory[s][0]
                if buy_amt > remaining:
                    # Partial use of this buy lot
                    used_amt = remaining
                    pnl_for_this_sell += (price - buy_price) * used_amt
                    new_buy_amt = buy_amt - used_amt
                    inventory[s][0] = (buy_time, new_buy_amt, buy_price)
                    remaining = 0
                else:
                    # Use the entire buy lot
                    used_amt = buy_amt
                    pnl_for_this_sell += (price - buy_price) * used_amt
                    inventory[s].pop(0)  # remove this buy lot
                    remaining -= used_amt

            total_pnl += pnl_for_this_sell

            # Future price analysis: check price after 24 hours
            future_time = t_time + datetime.timedelta(hours=24)
            future_price = get_token_price_at_time(s, future_time)
            if future_price and future_price > price:
                print(f"Selling {s} at ${price:.2f} was early. Future price after 24h: ${future_price:.2f}")
            elif future_price and future_price < price:
                print(f"Selling {s} at ${price:.2f} was good. Price dropped to ${future_price:.2f} after 24h")
            else:
                print(f"Selling {s} at ${price:.2f}. No future price data or stable price.")

    print(f"Total PnL: {total_pnl:.2f} USD")

def main():
    pubkey = "A8y3cs9NWGfuSfJkDuFY3abzSfVWcWwWz3HJgfz4qwWe"
    trades = process_transactions(pubkey, limit=5)
    compute_pnl_and_future_analysis(trades)

if __name__ == "__main__":
    main()
