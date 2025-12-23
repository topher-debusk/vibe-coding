from vibe_coding.utils import tool, ai_call


@tool(
    name="summarize",
    description="Summarize input text into a short summary",
    inputs=["text"],
    outputs=["summary"]
)
def summarize_text(text):
    """Summarize input text using AI"""
    return ai_call(text)
