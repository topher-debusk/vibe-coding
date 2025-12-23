import os
from vibe_coding.utils import TOOLS, load_state, save_state


def orchestrator(args):
    """Multi-step agent orchestration that runs tools in sequence"""
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
