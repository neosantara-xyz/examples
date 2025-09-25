# Multi-Agent Debate with Tools using Agno

This example demonstrates how to build a dynamic, multi-agent debate system using the [Agno](https://github.com/agno-agi/agno) framework. In this workflow, multiple autonomous AI agents take on different positions on a topic, use tools to gather evidence from the web, and engage in a structured debate moderated by another AI agent.

The entire process is streamed in real-time to your console, and a full transcript is saved as a Markdown file.

## How It Works

The system orchestrates the debate in a series of asynchronous steps:

1.  **Initialization**:

      * An `EfficientToolDebateSystem` is created with a `topic` and a list of `positions` (e.g., "Pro-regulation", "Anti-regulation").
      * An `Agent` is created for each position, instructed to be persuasive and use web search.
      * A neutral `Moderator` agent is also initialized to summarize and provide a final verdict.
      * All agents use the same underlying model (`nusantara-base` in this case) for consistency.

2.  **Image Analysis (Optional)**:

      * If an `image_context` URL is provided, the first agent performs a vision-based analysis. This analysis is then shared with other agents to inform their opening statements.

3.  **Opening Statements**:

      * Each agent generates and streams its opening argument based on its assigned position and instructions. The first agent also integrates the image analysis if available.

4.  **Debate Rounds**:

      * The debate proceeds for a set number of rounds.
      * In each round, every agent is given the most recent statement from its opponent to formulate a counter-argument.
      * Agents use their web search tool to find supporting data for their rebuttals.

5.  **Moderator Summaries**:

      * After each round, the `Moderator` agent analyzes the arguments presented and provides a brief, neutral summary of the key points and clashes.

6.  **Final Assessment**:

      * Once all rounds are complete, the `Moderator` provides a final, conclusive assessment of the entire debate, highlighting the strongest arguments and declaring a neutral verdict.

7.  **Transcript Generation**:

      * Throughout the process, all generated content is compiled into a single Markdown file, creating a complete and readable record of the debate.

## Getting Started

Follow these steps to run the agent debate system on your own machine.

### 1\. Prerequisites

  * Python 3.8+
  * An API key from an OpenAI-compatible service (the example is configured for [Neosantara AI](https://neosantara.xyz/)).

### 2\. Installation

Clone the repository and install the required Python packages:

```bash
# Clone the repository
git clone https://github.com/neosantara-xyz/examples
cd examples/agno/agent_debate

# Install dependency
pip install -r requirements.txt
```

### 3\. Set Environment Variables

You need to provide your API key as an environment variable. Create a file named `.env` in the root of your project directory:
```
NAI_API_KEY="YOUR_API_KEY_HERE"
```

The Python script will automatically load this variable.

### 4\. Run the Script

Execute the script from your terminal:

```bash
python main.py
```

You will see the debate unfold in real-time in your console. Once finished, you will find new file named `efficient_tool_debate.md`: The full, formatted debate transcript

## Customization

You can easily adapt this example for your own use cases:

  * **Change the Topic**: Modify the `topic` and `positions` variables in the `main` function to debate anything you want.

    ```python
    debate = EfficientToolDebateSystem(
        topic="Is remote work more productive than in-office work?",
        positions=["For Remote Work", "For In-Office Work"],
    )
    ```

  * **Add an Image**: To run a multi-modal debate, uncomment the `image_context` line and provide a public URL to an image.

    ```python
    debate = EfficientToolDebateSystem(
        # ...
        image_context="https://path.to/your/image.jpg"
    )
    ```

  * **Change the Model**: Swap `nusantara-base` with any other [Neosantara model](https://neosantara.xyz/models) that supported `function_calling` by changing the `id` in the `OpenAILike` configuration.

  * **Add More Tools**: Equip your agents with different tools from the Agno library or create your own to give them new capabilities.