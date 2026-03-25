from tools import get_stock_price
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

user_prompt = "What is Tesla stock price?"
system_prompt = """
You are a financial assistant.

If the user asks for stock price information,
you should call the tool 'get_stock_price'.

Return JSON like:

{
 "action": "tool_name",
 "input": "tool input"
}

If no tool is needed return:

{
 "action": "final_answer",
 "answer": "response"
}
"""


client = OpenAI(api_key=api_key)

tools = {
    "get_stock_price": get_stock_price
}

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    temperature=0.0,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

content = response.choices[0].message.content
content = content.replace("```json", "").replace("```", "").strip()
data = json.loads(content)
print("LLM response:", data)

if data["action"] == "get_stock_price":
    price = tools[data["action"]](data["input"]).get("price")
    print(f"Price of {data['input']} is {price}")
else:
    print(data["answer"])