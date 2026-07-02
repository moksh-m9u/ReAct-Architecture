# ReAct Agent Scaffold

<p align="left">
  <img src="https://img.shields.io/badge/Python-3670A0?style=flat-square&logo=python&logoColor=ffdd54" alt="Python" />
  <img src="https://img.shields.io/badge/🦜🔗_LangChain-1C3C3C?style=flat-square" alt="LangChain" />
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Anthropic-191919?style=flat-square&logo=anthropic&logoColor=white" alt="Anthropic" />
  <img src="https://img.shields.io/badge/Groq-F55036?style=flat-square" alt="Groq" />
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium" />
</p>

A plug-and-play Python harness for a [ReAct](https://arxiv.org/abs/2210.03629)-style agent. Drop a decorated function into `tools/`, set your model, and run.

---
## ReAct Architecture Research Paper : 
<img width="1348" height="1750" alt="image" src="https://github.com/user-attachments/assets/de5818eb-e7c8-49bb-98d9-d72931f3b285" />

---


## Quick start

```bash
# 1. Install dependencies
pip install langchain langchain-core python-dotenv langchain-openai

# 2. Copy the env file and add your API key
cp .env.example .env
# Edit .env — set OPENAI_API_KEY=sk-... at minimum

# 3. Run
python main.py
```

The script comes with a rigorous default system prompt built-in to enforce disciplined research and tool use. You'll be prompted for a goal (what you want it to do). The agent will reason, call tools, and return a final answer.

**Example Goal:**
> Research about topics which are discussed in the most in recent top published papers around agentic ai and make sure to compare at 3 of them

## How to add a new tool

Drop a new `.py` file into `tools/` with the exact pattern below:

```python
from langchain_core.tools import tool


@tool
def my_tool(param_one: str, param_two: int) -> str:
    """Describe what this tool does. This docstring becomes the tool description
    that the LLM sees, so be specific about when to use it and what it returns."""
    # Your logic here
    return f"Received {param_one} and {param_two}"
```

Rules:
- The function **must** have a **docstring** (used as the tool description).
- Every parameter **must** have a **type hint**.
- The tool is auto-discovered on next launch — zero registration needed.
- If a tool raises an exception at runtime, the error is caught and returned to the agent as a message so it can retry or route around it, instead of crashing.

Replace or remove the example files (`example_search.py`, `example_calculator.py`) with your own real tools.

## How to set the model

Edit `.env`:

```
MODEL=openai:gpt-4o
```

Format: `provider:model_name`

| Provider | Env format | Install |
|---|---|---|
| OpenAI | `openai:gpt-4o` | `pip install langchain-openai` |
| Anthropic | `anthropic:claude-sonnet-4-6` | `pip install langchain-anthropic` |
| Groq | `groq:qwen-qwq-32b` | `pip install langchain-groq` |
| Google | `google:gemini-2.0-flash` | `pip install langchain-google-genai` |

Set the corresponding API key in `.env` (e.g. `OPENAI_API_KEY=sk-...`).

## How to run

### Interactive mode
```bash
python main.py
```
If you don't provide a system prompt, it will fall back to a strict, built-in research persona. You'll then be asked for a goal:
`Goal (what should the agent do?): Research about topics which are discussed in the most in recent top published papers around agentic ai and make sure to compare at 3 of them`

### Non-interactive (CLI args)
```bash
# Using the default rigorous research prompt:
python main.py --goal "Research about topics which are discussed in the most in recent top published papers around agentic ai and make sure to compare at 3 of them"

# Or override with your own custom system prompt:
python main.py --system "You are a helpful math tutor." --goal "What is 2 + 2?"
```

## Configuration

All settings in `.env`:

| Variable | Default | Description |
|---|---|---|
| `MODEL` | `openai:gpt-4o` | Model in `provider:name` format |
| `MAX_STEPS` | `10` | Max tool-calling steps before the agent stops |
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Your Anthropic API key |
| `GROQ_API_KEY` | — | Your Groq API key |
| `GOOGLE_API_KEY` | — | Your Google AI API key |

## Project structure

```
agent-scaffold/
├── tools/
│   ├── __init__.py       # Auto-discovery: scans tools/*.py for @tool objects
│   ├── example_search.py # Example: simulated web search
│   └── example_calculator.py  # Example: safe arithmetic evaluator
├── config.py              # Reads MODEL, MAX_STEPS from .env
├── main.py                # Entry point: build agent, run loop, print answer
├── .env.example           # Template for .env
└── README.md
```

The agent uses `langchain.agents.create_agent` (not the deprecated `AgentExecutor`) and streams every step so you can watch it reason, call tools, and incorporate results before producing a final answer.
