import dspy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Neosantara API
# Neosantara is OpenAI-compatible
api_key = os.getenv("NEOSANTARA_API_KEY")
api_base = "https://api.neosantara.xyz/v1"
model = "claude-3-haiku" # or any model available on Neosantara

# Define the language model
# In DSPy 3.x, use dspy.LM with the provider/model format
lm = dspy.LM(f"openai/{model}", api_key=api_key, api_base=api_base)
dspy.settings.configure(lm=lm)

# Define a Signature for a simple QA task
class SimpleQA(dspy.Signature):
    """Answer questions with short, factual responses."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

# Define the module
class QABot(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.Predict(SimpleQA)
    
    def forward(self, question):
        return self.generate_answer(question=question)

# Use the module
def main():
    if not api_key:
        print("Please set NEOSANTARA_API_KEY in your .env file.")
        return

    qa = QABot()
    question = "What is the capital of Indonesia?"
    response = qa.forward(question=question)
    
    print(f"Question: {question}")
    print(f"Answer: {response.answer}")

if __name__ == "__main__":
    main()
