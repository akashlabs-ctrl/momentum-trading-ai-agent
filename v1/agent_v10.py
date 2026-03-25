from dotenv import load_dotenv
import os
from openai import OpenAI
from tools import (
    get_stock_price,
    get_volume_data,
    get_rsi,
    get_top_movers,
)
import asyncio

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
tools = {
    "get_stock_price": get_stock_price,
    "get_volume_data": get_volume_data,
    "get_rsi": get_rsi,
    "get_top_movers": get_top_movers
}

def compute_momentum_score(change_pct, rsi, volume):
    print("Computing momentum score for stock with change_pct:", change_pct, "rsi:", rsi, "volume:", volume)

    # normalize price change
    price_score = abs(change_pct) / 5
    price_score = min(price_score, 1)

    # RSI signal
    if rsi > 60:
        rsi_score = 1
    elif rsi > 50:
        rsi_score = 0.7
    elif rsi > 40:
        rsi_score = 0.4
    else:
        rsi_score = 0.2

    # normalize volume
    volume_score = min(volume / 20_000_000, 1)

    momentum_score = (
        0.5 * price_score +
        0.3 * rsi_score +
        0.2 * volume_score
    )

    return round(momentum_score, 3)

async def async_execute_tool(name, args):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, tools[name], args)
    return result

async def analyze_stocks_parallel(stocks):
    tasks = []
    for stock in stocks:
        ticker = stock["ticker"]
        tasks.append(async_execute_tool("get_stock_price", {"ticker": ticker}))
        tasks.append(async_execute_tool("get_volume_data", {"ticker": ticker}))
        tasks.append(async_execute_tool("get_rsi", {"ticker": ticker}))
    results = await asyncio.gather(*tasks)
    return results

async def parallel_analysis(state):

    stocks = state["stocks"]

    results = await analyze_stocks_parallel(state["stocks"])

    index = 0

    for stock in stocks:

        ticker = stock["ticker"]

        price = results[index]; index += 1
        volume = results[index]; index += 1
        rsi = results[index]; index += 1

        state["analysis"][ticker] = {
            "price": price["price"],
            "volume": volume["volume"]["volume"],
            "rsi": rsi["rsi"]["rsi"],
            "change_pct": stock["change_pct"]
        }

system_prompt = """
You are a quantitative trading analyst.

Your job is to analyze stock data and identify momentum signals.

You will receive structured data containing indicators such as:
- price movement
- RSI
- trading volume

Use this data to determine which stocks show the strongest momentum.

Guidelines:
- Base your analysis only on the provided data.
- Consider price movement, RSI, and volume together.
- Explain your reasoning clearly.
- Highlight the stocks with the strongest momentum signals.
"""

state = {
    "stocks": [],
    "analysis": {},
    "messages": []
}

state["messages"].append({
    "role": "system",
    "content": system_prompt
})

workflow_state = "SCAN_MARKET"
while workflow_state != "DONE":
    if workflow_state == "SCAN_MARKET":
        print("Scanning market for top movers...")
        movers = get_top_movers()
        state["stocks"] = movers
        print("Found top movers:", state["stocks"])
        workflow_state = "ANALYZE_STOCKS"
    elif workflow_state == "ANALYZE_STOCKS":
        for stock in state["stocks"]:
            print("Analyzing stock:", stock, stock["ticker"])
            ticker = stock["ticker"]
            stock_price = get_stock_price(stock["ticker"])
            stock_volume = get_volume_data(ticker)
            stock_rsi = get_rsi(ticker)
            print("Stock price:", stock_price)
            print("Stock volume:", stock_volume)
            print("Stock RSI:", stock_rsi)
            state["analysis"][ticker] = {
                "price": stock_price,
                "volume": stock_volume["volume"],
                "price_change_pct": stock["change_pct"],
                "rsi": stock_rsi["rsi"]
            }
        workflow_state = "SCORE"
    elif workflow_state == "SCORE":
        print("Scoring stocks...")
        for ticker, data in state["analysis"].items():
            score = compute_momentum_score(
                data["price_change_pct"],
                data["rsi"],
                data["volume"]
            )
            print("Stock", ticker, "score:", score)
            state["analysis"][ticker]["momentum_score"] = score
        workflow_state = "SUMMARIZE"
    elif workflow_state == "SUMMARIZE":
        print("Summarizing analysis...", state["analysis"].items())
        ranked = sorted(
            state["analysis"].items(),
            key=lambda x: x[1]["momentum_score"],
            reverse=True
        )
        promt =  f"""
        Here is analysis of stocks:

        {ranked}

        Identify the stock with the strongest momentum and explain why.
        """

        state["messages"].append({
            "role": "user",
            "content": promt
        })
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=state["messages"]
        )
        answer = response.choices[0].message.content

        print("Final answer:", answer)

        workflow_state = "DONE"