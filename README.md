# MomentumTrading

A small Python project for experimenting with momentum-based stock analysis using market data and an LLM summary step.

The project:

- pulls stock data with `yfinance`
- calculates RSI with `ta`
- finds top movers from a small watchlist
- scores stocks based on price change, RSI, and volume
- uses the OpenAI API to summarize the strongest momentum signals

## Project Structure

```text
MomentumTrading/
├── v1/
│   ├── tools.py
│   ├── agent_v1.py ... agent_v10.py
│   └── v8_langgraph.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- An OpenAI API key

Install the main dependencies:

```bash
pip install openai python-dotenv yfinance ta langgraph
```

## Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

The code uses `python-dotenv`, so the API key is loaded automatically from `.env`.

## How It Works

`v1/tools.py` provides helper functions to:

- fetch the latest stock price
- fetch recent volume
- calculate RSI
- identify the top movers from a predefined ticker list

The agent scripts in `v1/` build on those tools in slightly different ways as the project evolves.

Two notable scripts are:

- `v1/agent_v10.py`: a workflow that scans stocks, analyzes signals, computes a momentum score, and asks the model for a final explanation
- `v1/v8_langgraph.py`: a LangGraph-based version of the workflow

## Running The Project

From the `MomentumTrading` directory:

```bash
python v1/agent_v10.py
```

Or run the LangGraph version:

```bash
python v1/v8_langgraph.py
```

## Momentum Score

In `v1/agent_v10.py`, the momentum score is based on:

- price change percentage
- RSI strength
- trading volume

The current weighting is:

- 50% price change
- 30% RSI
- 20% volume

## Notes

- The watchlist in `v1/tools.py` is currently hardcoded.
- This project is for learning and experimentation, not financial advice.
- If `OPENAI_API_KEY` is missing, OpenAI client initialization will fail.
