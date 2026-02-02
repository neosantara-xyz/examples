import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Neosantara API based on official docs
# Neosantara recommends using the crewai.LLM class directly
api_key = os.getenv("NEOSANTARA_API_KEY") or os.getenv("NAI_API_KEY")
api_base = "https://api.neosantara.xyz/v1"
# The 'openai/' prefix is REQUIRED for OpenAI-compatible endpoints in CrewAI
model_id = "openai/claude-3-haiku" 

# Initialize the LLM
llm = LLM(
    model=model_id,
    api_key=api_key,
    base_url=api_base
)

# Define Agents
researcher = Agent(
    role='Tech Researcher',
    goal='Identify emerging trends in Indonesian AI landscape',
    backstory='You are an expert tech journalist specializing in Southeast Asian technology.',
    llm=llm,
    verbose=True
)

writer = Agent(
    role='Content Strategist',
    goal='Write a compelling blog post about AI in Indonesia',
    backstory='You are a skilled writer who can explain complex tech topics to a general audience.',
    llm=llm,
    verbose=True
)

# Define Tasks
task_research = Task(
    description='Research the current state of AI development in Indonesia for 2026.',
    expected_output='A summary of 3 key trends or major projects.',
    agent=researcher
)

task_write = Task(
    description='Based on the research, write a 2-paragraph blog post about Indonesia\'s AI future.',
    expected_output='A 2-paragraph blog post in English.',
    agent=writer
)

# Assemble the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[task_research, task_write],
    process=Process.sequential,
    verbose=True
)

# Start the work
def main():
    if not api_key:
        print("Please set NEOSANTARA_API_KEY in your .env file.")
        return

    print("### Starting CrewAI with Neosantara AI ###")
    result = crew.kickoff()
    print("\n\n########################")
    print("## FINAL RESULT ##")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    main()
