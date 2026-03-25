from dotenv import load_dotenv
import os
from openai import OpenAI
import json
from tools import get_stock_price

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
tools = {
    "get_stock_price": get_stock_price
}

system_prompt = """
You are a financial assistant.

If stock price data is needed, call the tool.

Return JSON:

Tool call format:
{
 "action": "get_stock_price",
 "input": "ticker"
}

Final answer format:
{
 "action": "final_answer",
 "answer": "response"
}
"""

user_prompt = "What is Tesla stock price?"


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    temperature=0.0,
    messages=messages
)

content = response.choices[0].message.content
content = content.replace("```json", "").replace("```", "").strip()

llm_decision = json.loads(content)
print("LLM decision:", llm_decision)

if llm_decision.get("action") in tools:
    tool_response = tools[llm_decision.get("action")](llm_decision.get("input"))
    print("Tool response:", tool_response)
    messages.append({
        "role": "assistant",
        "content": content
    })

    messages.append({
        "role": "user",
        "content": f"Tool returned this data: {json.dumps(tool_response)}. Now give final answer."
    })

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.0,
        messages=messages
    )

    response2 = response.choices[0].message.content
    response2 = response2.replace("```json", "").replace("```", "").strip()
    response2 = json.loads(response2)
    print("Final response:", response2.get("answer"))
else:
    print(llm_decision.get("answer"))