# DSPy Examples with Neosantara AI

This directory contains examples of using the [DSPy](https://github.com/stanfordnlp/dspy) framework with the **Neosantara AI API**.

DSPy is a framework for programming—rather than just prompting—language models. It allows you to define "Signatures" for your tasks and use "Modules" like `Predict` or `ChainOfThought` that can be automatically optimized.

## Prerequisites

1.  **Python 3.9+**
2.  **Neosantara API Key**: Get your key from the [Neosantara Dashboard](https://api.neosantara.xyz).

## Setup

1.  Create a virtual environment and install the required packages:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  Create a `.env` file in this directory and add your API key:
    ```env
    NEOSANTARA_API_KEY=your_api_key_here
    ```

## Examples

### 1. Simple Q&A (`simple_qa.py`)
A basic example showing how to define a signature for a simple question-answering task and use the `dspy.Predict` module.

```bash
source venv/bin/activate
python simple_qa.py
```

### 2. Chain of Thought (`chain_of_thought.py`)
Demonstrates how to use `dspy.ChainOfThought` to perform multi-step reasoning for a math problem.

```bash
source venv/bin/activate
python chain_of_thought.py
```

### 3. ReAct Agent (`react_agent.py`)
Shows how to build an autonomous agent using the `dspy.ReAct` module. The agent can use external tools (mocked in this example) to find information before answering.

```bash
source venv/bin/activate
python react_agent.py
```

## How it works with Neosantara

Since Neosantara AI is OpenAI-compatible, we can use the `dspy.LM` class (DSPy 3.x) by overriding the `api_base` and `api_key`. We use the `openai/` prefix to tell DSPy to use the OpenAI-compatible client.

```python
import dspy
lm = dspy.LM(
    "openai/claude-3-haiku", 
    api_key="your_key", 
    api_base="https://api.neosantara.xyz/v1"
)
dspy.settings.configure(lm=lm)
```

## Recommended Models

Neosantara AI provides a wide range of models. You can easily swap the `model` variable in the examples to try different capabilities:

### Agentic & Reasoning (Best for complex DSPy pipelines)
*   `kimi-k2` / `kimi-k2:research`: Optimized for agentic tasks, tool use, and deep research.
*   `glm-4.6`: SOTA performance on agent benchmarks and complex reasoning.
*   `deepseek-chat-v3.1`: High-performance 671B MoE model.
*   `llama-3.3-70b-instruct`: Very robust general-purpose reasoning.

### High Speed & Efficiency (Best for iterative optimization)
*   `garda-beta-mini`: Lightning fast, optimized for Indonesian and long contexts.
*   `gemini-3-flash`: Google's most intelligent model built for speed.
*   `claude-3-haiku`: Fast and highly affordable (used as default in these examples).

### Coding & Specialized
*   `qwen3-32b`: SOTA reasoning and multilingual support.
*   `archipelago-70b`: Fine-tuned for Indonesian cultural context and deep language nuance.

For a full list of available models, visit the [Neosantara Models Overview](https://docs.neosantara.xyz/en/models-overview).

