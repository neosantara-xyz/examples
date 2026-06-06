"""
Agno + Telegram interactive bot, powered by the Neosantara model provider.

This mirrors the interactive flow of E2B's OpenClaw Telegram example
(https://www.e2b.dev/docs/agents/openclaw/openclaw-telegram), but the agent is
built on Agno (https://docs.agno.com/tools/toolkits/social/telegram):

    Telegram user
        -> getUpdates long-poll (this runtime owns the *receive* side)
        -> Agno Agent on a Neosantara model
        -> TelegramTools.send_message (the *send* side)
        -> reply lands back in the user's chat.

Agno's TelegramTools only *sends* messages, so this script adds the receiving
loop via the Telegram Bot API getUpdates method.

Required env:
    TELEGRAM_TOKEN       Bot token from @BotFather.
    NEOSANTARA_API_KEY   Neosantara API key (the Neosantara model reads this).

Optional env:
    NEOSANTARA_MODEL     Model id (default: grok-4.1-fast-non-reasoning).
    AGENT_INSTRUCTIONS   System instructions for the agent.
    ALLOWED_CHAT_IDS     Comma-separated chat ids allowed to use the bot.
                         If unset, the bot replies to anyone who messages it.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

from agno.agent import Agent
from agno.models.neosantara import Neosantara
from agno.tools.telegram import TelegramTools

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
NEOSANTARA_API_KEY = os.environ.get("NEOSANTARA_API_KEY")
MODEL_ID = os.environ.get("NEOSANTARA_MODEL", "grok-4.1-fast-non-reasoning")
INSTRUCTIONS = os.environ.get(
    "AGENT_INSTRUCTIONS",
    "You are a helpful assistant chatting over Telegram. Keep replies concise.",
)
_allowed = os.environ.get("ALLOWED_CHAT_IDS", "").strip()
ALLOWED_CHAT_IDS = {c.strip() for c in _allowed.split(",") if c.strip()}

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
POLL_TIMEOUT = 30  # seconds for Telegram long-polling


def _require_env() -> None:
    missing = [
        name
        for name, val in (
            ("TELEGRAM_TOKEN", TELEGRAM_TOKEN),
            ("NEOSANTARA_API_KEY", NEOSANTARA_API_KEY),
        )
        if not val
    ]
    if missing:
        print(f"Missing required env: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def _api(method: str, params: dict) -> dict:
    """Call a Telegram Bot API method and return the parsed JSON result."""
    url = f"{API_BASE}/{method}?{urllib.parse.urlencode(params)}"
    # timeout slightly above POLL_TIMEOUT so long-poll requests aren't cut off.
    with urllib.request.urlopen(url, timeout=POLL_TIMEOUT + 10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_agent(chat_id: str) -> Agent:
    """Create an Agno agent bound to a specific Telegram chat for replies."""
    return Agent(
        name="telegram",
        model=Neosantara(id=MODEL_ID),
        tools=[TelegramTools(token=TELEGRAM_TOKEN, chat_id=chat_id)],
        instructions=INSTRUCTIONS,
        markdown=False,
    )


def handle_message(chat_id: str, text: str) -> None:
    """Run the agent for one incoming message; it replies via TelegramTools."""
    agent = build_agent(chat_id)
    # Tell the agent to deliver its answer through the send_message tool so the
    # reply lands back in the originating Telegram chat.
    agent.print_response(
        f"A Telegram user sent: {text!r}. "
        "Answer them and send the reply to the chat using your Telegram tool."
    )


def main() -> None:
    _require_env()
    print(f"Agno Telegram bot starting (model={MODEL_ID})...", flush=True)

    offset = None
    while True:
        try:
            params = {"timeout": POLL_TIMEOUT}
            if offset is not None:
                params["offset"] = offset
            data = _api("getUpdates", params)

            if not data.get("ok"):
                print(f"getUpdates error: {data}", file=sys.stderr, flush=True)
                time.sleep(3)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue

                text = message.get("text")
                chat = message.get("chat", {})
                chat_id = str(chat.get("id", ""))
                if not text or not chat_id:
                    continue

                if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
                    print(f"Ignoring chat_id {chat_id} (not allowed)", flush=True)
                    continue

                print(f"<- [{chat_id}] {text}", flush=True)
                try:
                    handle_message(chat_id, text)
                except Exception as exc:  # keep the loop alive on per-message errors
                    print(f"handle_message failed: {exc}", file=sys.stderr, flush=True)

        except KeyboardInterrupt:
            print("Shutting down.", flush=True)
            break
        except Exception as exc:
            print(f"poll loop error: {exc}", file=sys.stderr, flush=True)
            time.sleep(3)


if __name__ == "__main__":
    main()
