import httpx
import json

URL = "https://api.binance.com/api/v3/"


def serialize_params(params):
    """Convert parameters to the appropriate format for Binance API."""
    result = {}
    for key, value in params.items():
        if isinstance(value, list):
            result[key] = json.dumps(value)
        elif value is not None:
            result[key] = value
    return result


async def exchange_info_of_a_symbol(symbol):
    """Get exchange information for a specific symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}exchangeInfo", params={"symbol": symbol})
        return json.dumps(response.json())


async def exchange_info_of_all_symbols():
    """Get exchange information for all symbols."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}exchangeInfo")
        return response.json()


async def get_trade_data(symbol, interval, start_time=None, end_time=None, limit=None):
    """Get kline/candlestick data for a symbol."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": limit,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}klines", params={k: v for k, v in params.items() if v is not None}
        )
        return json.dumps(response.json())


async def agg_trades(symbol):
    """Get aggregate trades for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}aggTrades", params={"symbol": symbol, "limit": 20}
        )
        return json.dumps(response.json())


async def trade_history(symbol):
    """Get recent trades for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}historicalTrades", params={"symbol": symbol, "limit": 20}
        )
        return json.dumps(response.json())


async def depth(symbol):
    """Get order book depth for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}depth", params={"symbol": symbol})
        return json.dumps(response.json())


async def current_avg_price(symbol):
    """Get current average price for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}avgPrice", params={"symbol": symbol})
        return json.dumps(response.json())


async def price_ticker_in_24hr(symbol):
    """Get 24hr price ticker for a symbol."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}ticker/24hr", params={"symbol": symbol})
        return json.dumps(response.json())


async def trading_day_ticker(symbols):
    """Get trading day ticker for symbols."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{URL}ticker/tradingDay", params=serialize_params({"symbols": symbols})
        )
        return json.dumps(response.json())


async def symbol_price_ticker(symbol=None, symbols=None):
    """Get symbol price ticker."""
    params = serialize_params({"symbol": symbol, "symbols": symbols})
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}ticker/price", params=params)
        return json.dumps(response.json())


async def symbol_order_book_ticker(symbol=None, symbols=None):
    """Get symbol order book ticker."""
    params = serialize_params({"symbol": symbol, "symbols": symbols})
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}ticker/bookTicker", params=params)
        return json.dumps(response.json())


async def rolling_window_ticker(
    symbol=None, symbols=None, window_size=None, type_=None
):
    """Get rolling window price change statistics.

    Args:
        symbol: Symbol to get data for
        symbols: List of symbols to get data for
        window_size: Window size, e.g. "1d"
        type_: Type of response, either "FULL" or "MINI"
    """
    params = serialize_params(
        {"symbol": symbol, "symbols": symbols, "windowSize": window_size, "type": type_}
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL}ticker", params=params)
        return json.dumps(response.json())
