# CrewAI Examples with Neosantara AI

This directory contains examples of using the [CrewAI](https://github.com/crewAIInc/crewAI) multi-agent framework with the **Neosantara AI API**.

CrewAI allows you to orchestrate role-playing autonomous AI agents. By pointing CrewAI to Neosantara's OpenAI-compatible endpoint, you can power your agents with various models like `claude-3-haiku`, `kimi-k2`, or `llama-3.3-70b-instruct`.

## Setup

1.  Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  Configure your API key in a `.env` file:
    ```env
    NEOSANTARA_API_KEY=your_api_key_here
    ```

## Examples

### 1. Simple Crew (`simple_crew.py`)
A sequential workflow with two agents: a Researcher and a Writer. They work together to research and write about the AI landscape in Indonesia.

```bash
source venv/bin/activate
python simple_crew.py
```

## How it works with Neosantara

CrewAI works best with Neosantara by using the built-in `LLM` class. To use Neosantara, you need to:
1.  Use the `openai/` prefix for the model name (e.g., `openai/claude-3-haiku`).
2.  Point the `base_url` to `https://api.neosantara.xyz/v1`.

```python
from crewai import LLM

llm = LLM(
    model="openai/claude-3-haiku", 
    api_key="your_key",
    base_url="https://api.neosantara.xyz/v1"
)
```

## Recommended Models for CrewAI
For multi-agent workflows, models with strong instruction-following are recommended:
*   `openai/llama-3.3-70b-instruct`: Very robust and reliable.
*   `openai/kimi-k2`: Specialized for agentic tasks.
*   `openai/claude-3-sonnet`: Excellent balance of speed and intelligence.
