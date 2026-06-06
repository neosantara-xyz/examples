"""
Agno AgentOS Telegram interface — production-grade, powered by Neosantara.

Where `bot.py` is a minimal long-poll loop, this exposes the bot through Agno's
official AgentOS Telegram interface (FastAPI webhooks). You get streaming with
live edits, session management + /new /start /help commands, inbound media, and
group-chat support out of the box. It also serves the AgentOS API that the web
control plane at https://os.agno.com can connect to (Chat / Sessions / Memory).

Docs: https://docs.agno.com/agent-os/interfaces/telegram/introduction

This single file can run in three modes via AGENT_MODE:

  team      (default)  A Researcher + Writer multi-agent Team. The leader
                       delegates to a researcher (with web search) and a writer.
  agent                A single general-purpose agent.
  workflow             A two-step Draft -> Edit pipeline.

Required env:
    TELEGRAM_TOKEN                  Bot token from @BotFather.
    NEOSANTARA_API_KEY              Neosantara API key (read by the model).

Optional env:
    AGENT_MODE                      agent | team | workflow   (default: team)
    NEOSANTARA_MODEL                Model id (default: gemini-3-flash).
    PORT                            Port to serve on (default: 7777).
    APP_ENV                         "development" skips webhook secret checks.
    TELEGRAM_WEBHOOK_SECRET_TOKEN   Required in production.
    AGENT_INSTRUCTIONS              Override instructions (agent mode only).
    ENABLE_WEB_SEARCH               "true" gives the Researcher DuckDuckGo web
                                    search (team mode). Off by default since DDG
                                    can be rate-limited in some environments.
    SESSION_DB_FILE                 SQLite file (default: /tmp/telegram_sessions.db).

After starting, point Telegram's webhook at the server (see README):
    curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=${PUBLIC_URL}/telegram/webhook"
"""

import os

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.neosantara import Neosantara
from agno.os.app import AgentOS
from agno.os.interfaces.telegram import Telegram
from agno.team import Team
from agno.workflow.step import Step
from agno.workflow.steps import Steps
from agno.workflow.workflow import Workflow

MODE = os.environ.get("AGENT_MODE", "team").lower()
MODEL_ID = os.environ.get("NEOSANTARA_MODEL", "gemini-3-flash")
PORT = int(os.environ.get("PORT", "7777"))
SESSION_DB_FILE = os.environ.get("SESSION_DB_FILE", "/tmp/telegram_sessions.db")


def model() -> Neosantara:
    """A fresh Neosantara model instance (reads NEOSANTARA_API_KEY)."""
    return Neosantara(id=MODEL_ID)


def build_agent(db: SqliteDb) -> Agent:
    return Agent(
        name="Neosantara Telegram Bot",
        model=model(),
        db=db,
        instructions=[
            os.environ.get(
                "AGENT_INSTRUCTIONS",
                "You are a helpful assistant on Telegram. Keep responses concise and friendly.",
            )
        ],
        add_history_to_context=True,
        num_history_runs=3,
        add_datetime_to_context=True,
        markdown=True,
    )


def build_team(db: SqliteDb) -> Team:
    # Web search makes the Researcher stronger, but DuckDuckGo can be rate-limited
    # or blocked depending on the host's egress. It is opt-in via ENABLE_WEB_SEARCH
    # so the demo stays smooth by default; the team still coordinates without it.
    researcher_tools = []
    if os.environ.get("ENABLE_WEB_SEARCH", "false").lower() == "true":
        from agno.tools.duckduckgo import DuckDuckGoTools

        researcher_tools = [DuckDuckGoTools()]

    researcher = Agent(
        name="Researcher",
        model=model(),
        role="Researches topics and provides detailed factual information.",
        tools=researcher_tools,
        instructions=["Provide well-researched, factual information on the given topic."],
    )
    writer = Agent(
        name="Writer",
        model=model(),
        role="Takes research and writes clear, engaging summaries.",
        instructions=["Write concise, engaging summaries based on the research provided."],
    )
    return Team(
        name="Neosantara Research Team",
        model=model(),
        members=[researcher, writer],
        db=db,
        instructions=[
            "You coordinate a research team on Telegram.",
            "Use the Researcher to gather facts, then the Writer to craft the reply.",
            "Keep responses concise for Telegram.",
        ],
        add_history_to_context=True,
        num_history_runs=3,
        add_datetime_to_context=True,
        markdown=True,
    )


def build_workflow(db: SqliteDb) -> Workflow:
    drafter = Agent(
        name="Drafter",
        model=model(),
        instructions="Draft a response to the user's message. Be helpful and informative.",
    )
    editor = Agent(
        name="Editor",
        model=model(),
        instructions=[
            "Review and polish the draft for clarity and conciseness.",
            "Keep it short and suitable for a Telegram message.",
        ],
    )
    return Workflow(
        name="Neosantara Draft-Edit Workflow",
        description="A two-step workflow that drafts then edits responses for Telegram.",
        steps=[
            Steps(
                name="draft_and_edit",
                description="Draft then edit a response",
                steps=[
                    Step(name="draft", agent=drafter, description="Draft an initial response"),
                    Step(name="edit", agent=editor, description="Edit and polish the draft"),
                ],
            )
        ],
        db=db,
    )


db = SqliteDb(session_table="telegram_sessions", db_file=SESSION_DB_FILE)

if MODE == "agent":
    entity = build_agent(db)
    agent_os = AgentOS(agents=[entity], interfaces=[Telegram(agent=entity)])
elif MODE == "workflow":
    entity = build_workflow(db)
    agent_os = AgentOS(workflows=[entity], interfaces=[Telegram(workflow=entity)])
else:  # default: team
    entity = build_team(db)
    agent_os = AgentOS(teams=[entity], interfaces=[Telegram(team=entity)])

app = agent_os.get_app()

if __name__ == "__main__":
    print(f"Starting AgentOS Telegram interface in '{MODE}' mode (model={MODEL_ID})...")
    agent_os.serve(app="agentos_server:app", host="0.0.0.0", port=PORT)
