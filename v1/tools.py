import yfinance as yf
from ta.momentum import RSIIndicator

def get_stock_price(ticker):
    stock = yf.Ticker(ticker) 
    data = stock.history(period="1d")

    if data.empty:
        return {"error": "No data found"}
    
    price = float(data["Close"].iloc[-1])

    return {"price": price, "ticker": ticker}

def get_volume_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d")

    if data.empty:
        return {"error": "No data"}

    volume = int(data["Volume"].iloc[-1])

    return {
        "ticker": ticker,
        "volume": volume
    }

def get_rsi(ticker):

    stock = yf.Ticker(ticker)
    data = stock.history(period="3mo")

    if data.empty:
        return {"error": "No data"}

    rsi = RSIIndicator(close=data["Close"]).rsi()

    latest_rsi = float(rsi.iloc[-1])

    return {
        "ticker": ticker,
        "rsi": round(latest_rsi, 2)
    }

def get_top_movers():

    tickers = ["TSLA", "AAPL", "NVDA", "META", "AMZN"]

    movers = []

    for t in tickers:
        stock = yf.Ticker(t)
        data = stock.history(period="2d")

        if len(data) < 2:
            continue

        change = (data["Close"].iloc[-1] - data["Close"].iloc[-2]) / data["Close"].iloc[-2]

        movers.append({
            "ticker": t,
            "change_pct": round(float(change) * 100, 2)
        })

    movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

    return movers[:3]

def tools_schema():
    return [
    {
        "type": "function",
        "function": {
            "name": "get_rsi",
            "description": "Get the RSI indicator for a stock ticker",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_volume_data",
            "description": "Get the latest trading volume",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_movers",
            "description": "Get stocks with biggest price moves today",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
        }
    ]