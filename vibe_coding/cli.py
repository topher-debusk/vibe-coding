import argparse
import os
from vibe_coding.utils import TOOLS, load_state, save_state
from vibe_coding.tools.summarize import summarize_text
from vibe_coding.tools.todo import generate_todos
from vibe_coding.orchestrator import orchestrator


# ----------------------
# Command handlers
# ----------------------
def summarize(args):
    """Handle summarize command"""
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
    """Generate todo list from text"""
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
# CLI entry point
# ----------------------
def main():
    """Parse arguments and run the appropriate command"""
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


if __name__ == "__main__":
    # Print registered tools at startup
    print("Registered tools:", list(TOOLS.keys()))
    main()
