import dspy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Neosantara API
api_key = os.getenv("NEOSANTARA_API_KEY")
api_base = "https://api.neosantara.xyz/v1"
model = "claude-3-haiku"

# Define the language model (DSPy 3.x syntax)
lm = dspy.LM(f"openai/{model}", api_key=api_key, api_base=api_base)
dspy.settings.configure(lm=lm)

# Define a simple search tool (Mock)
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    # In a real app, this would call an API
    knowledge_base = {
        "Neosantara AI": "Neosantara AI is a unified LLM gateway from Indonesia that supports multiple providers like OpenAI, Anthropic, and Google.",
        "DSPy": "DSPy is a framework for programming with language models, developed by Stanford NLP.",
        "Jakarta": "Jakarta is the capital and largest city of Indonesia."
    }
    print(f"--- Tool Call: Searching Wikipedia for '{query}' ---")
    return knowledge_base.get(query, "No information found.")

# Define a Signature for the agent
class AgentSignature(dspy.Signature):
    """Answer questions using available tools."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="factual answer based on tool output")

# Define the ReAct Agent
class ToolAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # Initialize ReAct with the signature and tools
        self.agent = dspy.ReAct(AgentSignature, tools=[search_wikipedia])
    
    def forward(self, question):
        return self.agent(question=question)

def main():
    if not api_key:
        print("Please set NEOSANTARA_API_KEY in your .env file.")
        return

    agent = ToolAgent()
    question = "What is Neosantara AI?"
    
    print(f"Question: {question}")
    # Use the __call__ method (recommended over .forward)
    response = agent(question=question)
    
    print(f"\nFinal Answer: {response.answer}")

if __name__ == "__main__":
    main()
