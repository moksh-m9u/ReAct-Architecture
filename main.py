import argparse
import sys

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError

from config import MODEL, MAX_STEPS
from tools import discover_tools


def print_event(event):
    messages = event.get("messages", [])
    if not messages:
        return
    msg = messages[-1]

    if isinstance(msg, AIMessage):
        if msg.content:
            print(f"\n  {msg.content}")
        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                print(f"\n  >> Tool: {tc['name']}({args})")
    elif isinstance(msg, ToolMessage):
        preview = str(msg.content)[:250]
        print(f"\n  << {msg.name} returned: {preview}")


def main():
    parser = argparse.ArgumentParser(description="ReAct Agent - plug-and-play")
    parser.add_argument("--system", "-s", help="System prompt / agent persona")
    parser.add_argument("--goal", "-g", help="The goal or task for this run")
    args = parser.parse_args()

    system_prompt = args.system
    goal = args.goal

    if not system_prompt:
        print("\nUsing default rigorous research prompt...")
        system_prompt = """You are an AI researcher. Follow this process strictly:

1. Use web_search to find candidate papers — snippets alone are not sufficient evidence.
2. For every paper you plan to cite or compare, use scrape_pages_dynamic to read its
   actual content before making claims about it.
3. NEVER state a specific number, metric, arXiv ID, author name, or paper title unless
   it appears verbatim in a tool result from this run.
4. If a tool call fails or returns insufficient information, do NOT invent details to
   fill the gap. Either retry with a different query/tool, or explicitly tell the user
   you could only verify N of the requested items and stop there — a partial, honest
   answer is always correct over a complete, fabricated one.
5. Cite the source (URL) for every claim in your final answer."""

    if not goal:
        goal = input("Goal (what should the agent do?): ").strip()

    if not system_prompt or not goal:
        print("Both system prompt and goal are required.")
        sys.exit(1)

    print(f"\nLoading model: {MODEL}")
    model = ChatGroq(
        model=MODEL,
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
    )

    print("Discovering tools...")
    tools = discover_tools()
    print(f"Found {len(tools)} tools: {[t.name for t in tools]}")

    print("Building agent...")
    try:
        from langchain.agents import create_agent
    except ImportError:
        print(
            "Error: 'create_agent' not found in langchain.agents. "
            "Upgrade langchain: pip install 'langchain>=0.3'"
        )
        sys.exit(1)

    agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)

    last_event = None
    print(f"\n--- Running (max {MAX_STEPS} tool steps) ---")
    try:
        for event in agent.stream(
            {"messages": [HumanMessage(content=goal)]},
            config={"recursion_limit": MAX_STEPS * 2 + 1},
            stream_mode="values",
        ):
            last_event = event
            print_event(event)
    except GraphRecursionError:
        print(f"\n\n[Reached max steps ({MAX_STEPS}) - agent stopped.]")
        return
    except Exception as e:
        print(f"\n\n[Error: {e}]")
        return

    if last_event:
        final = last_event["messages"][-1]
        if isinstance(final, AIMessage) and final.content:
            print(f"\n=== Final Answer ===\n{final.content}")
        else:
            print("\n[Agent produced no final answer.]")


if __name__ == "__main__":
    main()
