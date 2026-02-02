import dspy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Neosantara API
api_key = os.getenv("NEOSANTARA_API_KEY")
api_base = "https://api.neosantara.xyz/v1"
model = "claude-3-haiku"

# Define the language model
# In DSPy 3.x, use dspy.LM with the provider/model format
lm = dspy.LM(f"openai/{model}", api_key=api_key, api_base=api_base)
dspy.settings.configure(lm=lm)

# Define a Signature for complex reasoning
class MathReasoning(dspy.Signature):
    """Solve math word problems with step-by-step reasoning."""
    problem = dspy.InputField()
    reasoning = dspy.OutputField(desc="step-by-step logic")
    answer = dspy.OutputField(desc="the final numeric or short answer")

# Define the module using ChainOfThought
class MathSolver(dspy.Module):
    def __init__(self):
        super().__init__()
        self.solve = dspy.ChainOfThought(MathReasoning)
    
    def forward(self, problem):
        return self.solve(problem=problem)

def main():
    if not api_key:
        print("Please set NEOSANTARA_API_KEY in your .env file.")
        return

    solver = MathSolver()
    problem = "If I have 5 apples and buy 3 more, then give half to my friend, how many do I have left?"
    response = solver.forward(problem=problem)
    
    print(f"Problem: {problem}")
    print(f"Reasoning: {response.reasoning}")
    print(f"Answer: {response.answer}")

if __name__ == "__main__":
    main()
