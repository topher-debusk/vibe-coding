import openai
import os
import json

STATE_FILE = "agent_state.json"

# ----------------------
# State management
# ----------------------
def save_state(data):
    """Save state to JSON file"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Warning: Could not save state ({e})")

def load_state():
    """Load state from JSON file"""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# ----------------------
# AI integration
# ----------------------
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

# ----------------------
# Tool registry and decorator
# ----------------------
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
