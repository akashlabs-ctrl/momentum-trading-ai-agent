from typing import TypedDict, Dict, List
from tools import get_top_movers, get_stock_price as get_price, get_rsi, get_volume_data as get_volume_data
from openai import OpenAI
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AgentState(TypedDict):
    stocks: List[Dict]
    analysis: Dict[str, Dict]
    result: str

def scan_market(state: AgentState):
    print("Scanning market for top movers...")

    movers = get_top_movers()

    return {
        "stocks": movers
    }

def analyze_stocks(state: AgentState):

    print("Analyzing stocks...")

    analysis = {}

    for stock in state["stocks"]:

        ticker = stock["ticker"]

        price = get_price(ticker)
        rsi = get_rsi(ticker)
        volume = get_volume_data(ticker)

        analysis[ticker] = {
            "price": price["price"],
            "rsi": rsi["rsi"],
            "volume": volume["volume"],
            "change_pct": stock["change_pct"]
        }

    return {
        "analysis": analysis
    }

def summarize(state: AgentState):

    print("Summarizing...")

    prompt = f"""
        Use ALL indicators:
        - price change
        - RSI
        - volume

        RSI rules:
        - >60 → strong upward
        - <40 → strong downward

        Data:
        {state["analysis"]}
        """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a quantitative trading analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "result": response.choices[0].message.content
    }

builder = StateGraph(AgentState)

builder.add_node("scan", scan_market)
builder.add_node("analyze", analyze_stocks)
builder.add_node("summarize", summarize)

builder.set_entry_point("scan")

builder.add_edge("scan", "analyze")
builder.add_edge("analyze", "summarize")

graph = builder.compile()

result = graph.invoke({
    "stocks": [],
    "analysis": {},
    "result": ""
})

print("\nFinal Output:\n", result["result"])