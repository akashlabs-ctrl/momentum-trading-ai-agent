from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from tools import (
    get_stock_price,
    get_volume_data,
    get_rsi,
    get_top_movers
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
tools = {
    "get_stock_price": get_stock_price,
    "get_volume_data": get_volume_data,
    "get_rsi": get_rsi,
    "get_top_movers": get_top_movers
}

system_prompt = """
You are a quantitative trading assistant.

You have access to these tools:

get_top_movers() → returns stocks with biggest daily moves
get_stock_price(ticker) → latest stock price
get_volume_data(ticker) → latest trading volume
get_rsi(ticker) → RSI indicator

Use tools to investigate stocks before answering.

Return JSON:

Tool call:
{
 "action": "tool_name",
 "input": "argument"
}

Final answer:
{
 "action": "final_answer",
 "answer": "analysis"
}
"""

user_prompt =  "Find a stock with strong momentum today"


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.0,
        messages=messages
    )

    content = response.choices[0].message.content
    print("llm decision:", content)
    content = content.replace("```json", "").replace("```", "").strip()
    llm_decision = json.loads(content)
    
    if llm_decision.get("action") in tools:
        if llm_decision.get("action") == "get_top_movers":
            tool_response = tools[llm_decision.get("action")]()
        else:
            tool_response = tools[llm_decision.get("action")](llm_decision.get("input"))
        print("Tool response:", tool_response)
        messages.append({
            "role": "assistant",
            "content": content
        })
        messages.append({
            "role": "user",
            "content": f"Tool returned this data: {json.dumps(tool_response)}."
        })
    elif llm_decision.get("action") == "final_answer":
        print(llm_decision.get("answer"))
        break
    else:
        print("Invalid action")
        break
