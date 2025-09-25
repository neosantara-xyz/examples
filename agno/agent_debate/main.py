import asyncio
import logging
from datetime import datetime
import os
from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools

# Minimal logging
logging.basicConfig(
    filename="debate_observability.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

class EfficientToolDebateSystem:
    def __init__(self, topic, positions, image_context=None):
        self.topic = topic
        self.positions = positions
        self.image_context = image_context
        self.debate_history = []
        self.agents = {}

        # Use nusantara-base for tool support (text + vision, low cost)
        api_key = os.environ.get("NAI_API_KEY")
        base_url = "https://api.neosantara.xyz/v1"

        for position in positions:
            self.agents[position] = Agent(
                model=OpenAILike(
                    id="nusantara-base",  # Supports tools, vision, JSON
                    api_key=api_key,
                    base_url=base_url
                ),
                tools=[DuckDuckGoTools()],
                markdown=True,
                instructions=f"You are debating: {topic}. Position: {position}. Use web search for evidence. Analyze image if provided. Keep responses <70 words, persuasive, and counter opponents."
            )

        # Moderator uses same model for consistency
        self.moderator = Agent(
            model=OpenAILike(
                id="nusantara-base",
                api_key=api_key,
                base_url=base_url
            ),
            tools=[DuckDuckGoTools()],  # Optional for fact-checking summaries
            markdown=True,
            instructions="Neutral moderator: Summarize arguments fairly, highlight strengths/weaknesses. Max 40 words per summary."
        )
        logging.info(f"Debate init: {topic}, model: nusantara-base (tools enabled)")

    async def start_debate(self, rounds=2):
        """Efficient debate with tools and streaming"""
        logging.info(f"Starting {rounds}-round debate: {self.topic}")
        markdown_output = f"# Efficient Tool Debate: {self.topic}\n\n**Model:** nusantara-base (Tools: Web Search)\n\n"

        # Merge image analysis into first opening (saves a call)
        image_analysis = ""
        if self.image_context:
            logging.info(f"Analyzing image: {self.image_context}")
            image_prompt = f"Briefly analyze this image for '{self.topic}': {self.image_context}."
            async for chunk in self.agents[self.positions[0]].arun(image_prompt, stream=True):
                if chunk.content:  # Check if content is not None
                    print(chunk.content, end="", flush=True)
                    image_analysis += chunk.content
            markdown_output += f"## Image Analysis\n![Image]({self.image_context})\n{image_analysis}\n\n"
            logging.info("Image analysis done")

        # Opening statements
        markdown_output += "## Openings\n"
        for position in self.positions:  # Fixed: use self.positions
            logging.info(f"Streaming opening: {position}")
            prompt = (
                f"Opening on '{self.topic}' ({position}). Include image: {image_analysis}." if image_analysis and position == self.positions[0] else
                f"Opening on '{self.topic}' ({position}). Use web search for evidence."
            )
            markdown_output += f"### {position}\n"
            opening = ""
            async for chunk in self.agents[position].arun(prompt, stream=True):
                if chunk.content: # Check if content is not None
                    print(chunk.content, end="", flush=True)
                    opening += chunk.content
            markdown_output += opening + "\n\n"
            self.debate_history.append({
                "round": 0,
                "position": position,
                "statement": opening.strip()
            })
            logging.info(f"Opening done: {position}")

        # Debate rounds
        for round_num in range(1, rounds + 1):
            markdown_output += f"## Round {round_num}\n"
            for position in self.positions:
                logging.info(f"Streaming argument: {position}, round {round_num}")
                recent_opponent = next(
                    (entry["statement"][:100] for entry in self.debate_history[-1:] if entry["position"] != position),
                    ""
                )
                prompt = (
                    f"Topic: {self.topic} | Position: {position}\n"
                    f"Recent opponent: {recent_opponent}\n"
                    f"Counter and reinforce with web evidence (<70 words)."
                )
                markdown_output += f"### {position}\n"
                argument = ""
                async for chunk in self.agents[position].arun(prompt, stream=True):
                    if chunk.content: # Check if content is not None
                        print(chunk.content, end="", flush=True)
                        argument += chunk.content
                markdown_output += argument + "\n\n"
                self.debate_history.append({
                    "round": round_num,
                    "position": position,
                    "statement": argument.strip()
                })
                logging.info(f"Argument done: {position}, round {round_num}")

            # Moderator summary
            logging.info(f"Streaming summary: round {round_num}")
            recent_args = "\n".join([f"{e['position']}: {e['statement'][:50]}..." for e in self.debate_history[-len(self.positions):]])
            prompt = f"Summarize Round {round_num} on '{self.topic}':\n{recent_args}\n<40 words."
            markdown_output += "### Moderator\n"
            summary = ""
            async for chunk in self.moderator.arun(prompt, stream=True):
                if chunk.content: # Check if content is not None
                    print(chunk.content, end="", flush=True)
                    summary += chunk.content
            markdown_output += summary + "\n\n"
            self.debate_history.append({
                "round": round_num,
                "position": "Moderator",
                "statement": summary.strip()
            })
            logging.info(f"Summary done: round {round_num}")

        # Final assessment
        logging.info("Streaming final assessment")
        recent_history = "\n".join([f"{e['position']}: {e['statement'][:80]}..." for e in self.debate_history[-4:]])
        prompt = f"Final analysis of '{self.topic}' debate:\n{recent_history}\nKey arguments, strengths, gaps, neutral verdict (<80 words)."
        markdown_output += "## Final Assessment\n"
        assessment = ""
        async for chunk in self.moderator.arun(prompt, stream=True):
            if chunk.content: # Check if content is not None
                print(chunk.content, end="", flush=True)
                assessment += chunk.content
        markdown_output += assessment + "\n"
        logging.info("Final assessment done")

        # Save output
        with open("efficient_tool_debate.md", "w") as f:
            f.write(markdown_output)

        print("\nDebate complete! Transcript: efficient_tool_debate.md")
        return {"topic": self.topic, "positions": self.positions, "transcript": markdown_output}

# Example usage
async def main():
    debate = EfficientToolDebateSystem(
        topic="Should AI development be regulated?",
        positions=["Pro-regulation", "Anti-regulation"],
       # image_context="https://example.com/image.png"  # Optional Multi-modal input
    )
    await debate.start_debate(rounds=2)

await main()