from vibe_coding.utils import tool


@tool(
    name="todo",
    description="Generate a todo list from text",
    inputs=["text"],
    outputs=["todos"]
)
def generate_todos(text):
    """Generate todo list from text by splitting on periods"""
    lines = [s.strip() for s in text.split(".") if s.strip()]
    return [f"- {line}" for line in lines]
