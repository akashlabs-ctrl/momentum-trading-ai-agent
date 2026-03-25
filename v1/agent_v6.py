from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from tools import (
    get_stock_price,
    get_volume_data,
    get_rsi,
    get_top_movers,
    tools_schema
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
You are a quantitative trading research assistant.

Your job is to analyze stocks for momentum signals.

You have access to tools that can:
- find top moving stocks
- retrieve RSI indicators
- retrieve trading volume

Guidelines:
- Use tools whenever market data is required.
- Investigate stocks before giving conclusions.
- Combine multiple signals (price movement, RSI, volume) to evaluate momentum.
- Do not guess market data. Always call tools when needed.

RSI interpretation:
- RSI > 70 → overbought
- RSI < 30 → oversold
- RSI 40–60 → neutral momentum

When enough information is gathered, provide a clear final analysis of the stock's momentum.
"""

user_prompt =  "Find a stock with strong momentum today"

planning_prompt =  """
You are a quantitative trading assistant.

Before using any tools, create a short investigation plan.

You have access to these tools.

Rules:
- Do NOT call any tools yet
- Only describe the investigation steps
- Reference the tools you may use
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    {"role": "user", "content": planning_prompt}
]

plan_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    temperature=0,
    messages=messages,
    tools=tools_schema(),
    tool_choice="none"
)

plan = plan_response.choices[0].message.content

print("Generated Plan:\n", plan)

messages.append({"role": "assistant", "content": plan})
messages.append({
    "role": "user",
    "content": "Proceed with executing the plan using the available tools."
})

while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.0,
        messages=messages,
        tools=tools_schema()
    )

    content = response.choices[0].message.content
    print("llm conetnt:", content)
    tool_calls = response.choices[0].message.tool_calls
    print("llm tool calls requested:", tool_calls)
    if tool_calls:
        messages.append(response.choices[0].message)
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            result = tools[tool_name](**tool_input)
            print("Tool result:", result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    else:
        print("Final answer:", content)
        break
