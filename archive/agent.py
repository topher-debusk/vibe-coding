import argparse
import openai
import os
import json
from types import SimpleNamespace

STATE_FILE = "agent_state.json"

# ----------------------
# Utility functions
# ----------------------
def save_state(data):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Warning: Could not save state ({e})")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def ai_call(prompt):
    """Try OpenAI API; fallback to stub if unavailable"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai.api_key = api_key
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            print("AI quota exceeded — using stub.")
        except Exception as e:
            print(f"OpenAI call failed ({e}) — using stub.")

    # Stub fallback
    return prompt.split(".")[0] + "."

TOOLS = {}

def tool(name, description="", inputs=None, outputs=None):
    """Decorator to register a tool with metadata"""
    def wrapper(func):
        TOOLS[name] = {
            "fn": func,
            "description": description,
            "inputs": inputs or [],
            "outputs": outputs or []
        }
        return func
    return wrapper

# ----------------------
# Pure logic functions (no CLI, no files)
# ----------------------

@tool(
    name="summarize",
    description="Summarize input text into a short summary",
    inputs=["text"],
    outputs=["summary"]
)
def summarize_text(text):
    return ai_call(text)


@tool(
    name="todo",
    description="Generate a todo list from text",
    inputs=["text"],
    outputs=["todos"]
)
def generate_todos(text):
    lines = [s.strip() for s in text.split(".") if s.strip()]
    return [f"- {line}" for line in lines]

# ----------------------
# Commands
# ----------------------
def summarize(args):
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return

    with open(args.input, "r") as f:
        content = f.read()

    summary = summarize_text(content)
    print(summary)

    state = load_state()
    state["last_summary"] = summary
    save_state(state)

def todo(args):
    """Generate todo list from text (stub)"""
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return

    with open(args.input, "r") as f:
        content = f.read()

    todos = generate_todos(content)
    print("Generated TODOs:")
    print("\n".join(todos))

    state = load_state()
    state["last_todo"] = todos
    save_state(state)

# ----------------------
# Multi-step agent orchestration
# ----------------------
def orchestrator(args):
    print("=== Orchestrator Starting ===")

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return

    with open(args.input, "r") as f:
        content = f.read()

    state = {}
    # Call all tools in the order you want
    for tool_name in ["summarize", "todo"]:
        tool_entry = TOOLS.get(tool_name)
        if not tool_entry:
            print(f"Tool not found: {tool_name}")
            continue

        result = tool_entry["fn"](content)
        state[tool_name] = result
        # Use output of summarize as input to todo
        content = result if tool_name == "summarize" else content

    # Print results
    print("\nSummary:")
    print(state.get("summarize", ""))

    print("\nTodos:")
    print("\n".join(state.get("todo", [])))

    # Save state
    saved_state = load_state()
    saved_state.update(state)
    save_state(saved_state)

    print("=== Orchestrator Finished ===")

# ----------------------
# CLI entry point
# ----------------------
def main():
    parser = argparse.ArgumentParser(prog="agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Summarize
    summarize_parser = subparsers.add_parser("summarize")
    summarize_parser.add_argument("input", help="path to input file")
    summarize_parser.set_defaults(func=summarize)

    # TODO
    todo_parser = subparsers.add_parser("todo")
    todo_parser.add_argument("input", help="path to input file")
    todo_parser.set_defaults(func=todo)

    # Orchestrator
    orchestrator_parser = subparsers.add_parser("orchestrate")
    orchestrator_parser.add_argument("input", help="path to input file")
    orchestrator_parser.set_defaults(func=orchestrator)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error running command: {e}")

# ----------------------
# Temporary test: list registered tools
# ----------------------
print("Registered tools:", list(TOOLS.keys()))

if __name__ == "__main__":
    main()