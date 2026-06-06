# Agno Telegram Bot on E2B (Neosantara)

An interactive Telegram bot built with the [Agno](https://github.com/agno-agi/agno) framework and powered by the **Neosantara** model provider, packaged as a reusable [E2B](https://e2b.dev) sandbox template.

It mirrors the flow of E2B's [OpenClaw Telegram example](https://www.e2b.dev/docs/agents/openclaw/openclaw-telegram): you run the agent inside an E2B sandbox, attach your bot token, and chat with it on Telegram.

## How It Works

This example ships **two runtimes** — pick the one that fits your needs:

### Option A — `bot.py` (simple long-poll)

Mirrors E2B's OpenClaw flow. Agno's [`TelegramTools`](https://docs.agno.com/tools/toolkits/social/telegram) toolkit only **sends** messages, so `bot.py` adds the **receive** side using the Telegram Bot API `getUpdates` long-poll loop:

```
Telegram user
    -> getUpdates long-poll        (bot.py owns the receive side)
    -> Agno Agent on Neosantara    (model=Neosantara(id=...))
    -> TelegramTools.send_message  (the send side)
    -> reply lands back in the user's chat
```

No public URL needed — easiest to run. Best for a quick single-user bot.

### Option B — `agentos_server.py` (AgentOS interface, production-grade)

Uses Agno's official [AgentOS Telegram interface](https://docs.agno.com/agent-os/interfaces/telegram/introduction) — a FastAPI **webhook** server that gives you, out of the box:

- token-by-token **streaming** with live message edits
- **session management** + `/new`, `/start`, `/help` commands (backed by SQLite)
- inbound **media** (photos, voice, audio, video, documents, stickers)
- **group-chat** support (@mention / reply gating)

This needs a **public URL** and a Telegram `setWebhook` call (see step 5B).

## 🚀 Quick Start (Google Colab)

The fastest way to try this is the cookbook notebook — it installs everything, builds the template, and launches the bot end to end, no local setup required:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neosantara-xyz/examples/blob/main/cookbook/advanced/agno-telegram-e2b.ipynb)

See [`cookbook/advanced/agno-telegram-e2b.ipynb`](../../cookbook/advanced/agno-telegram-e2b.ipynb). The local instructions below are for running it on your own machine instead.

## Getting Started (Local)

### 1. Prerequisites

- Python 3.8+
- A Telegram bot token from [@BotFather](https://t.me/BotFather) (run `/newbot`).
- A [Neosantara API key](https://api.neosantara.xyz).
- An [E2B API key](https://e2b.dev/dashboard).

### 2. Installation

```bash
git clone https://github.com/neosantara-xyz/examples
cd examples/agno/telegram_bot

pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Agno's `Neosantara` model reads `NEOSANTARA_API_KEY` automatically and defaults to `https://api.neosantara.xyz/v1` — no manual `base_url` needed.

### 4. Build the E2B Template

You can build the template two ways — pick one:

**Option A — Python SDK (no local Docker):**

```bash
export E2B_API_KEY=...   # or rely on your .env
python build_template.py
```

**Option B — E2B CLI + Dockerfile:**

```bash
e2b template build --name agno-telegram --dockerfile e2b.Dockerfile
```

Both produce a template named `agno-telegram` on E2B infrastructure.

### 5. Run the Bot in a Sandbox

Create the sandbox once, then start **either** runtime inside it.

```python
from e2b import Sandbox

sbx = Sandbox.create(
    "agno-telegram",
    envs={
        "TELEGRAM_TOKEN": "<bot-token-from-BotFather>",
        "NEOSANTARA_API_KEY": "<your-neosantara-key>",
    },
    timeout=3600,
)
```

**5A — Option A: long-poll bot (no public URL)**

```python
sbx.commands.run("python /app/bot.py", background=True)
```

Now open your bot in Telegram, send it a message, and the Agno agent replies.

**5B — Option B: AgentOS webhook server**

```python
PORT = 7777
sbx.commands.run(
    f"APP_ENV=development PORT={PORT} python /app/agentos_server.py",
    background=True,
)

# Expose the port and point Telegram's webhook at it
public_url = sbx.get_host(PORT)  # e.g. "7777-<id>.e2b.app"
sbx.commands.run(
    f'curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook'
    f'?url=https://{public_url}/telegram/webhook"',
    envs={"TELEGRAM_TOKEN": "<bot-token-from-BotFather>"},
)
```

Then message your bot — you'll get streaming replies, `/new` `/help` commands, media, and group support. In production, set `TELEGRAM_WEBHOOK_SECRET_TOKEN` (instead of `APP_ENV=development`) and pass a matching `&secret_token=` to `setWebhook`.

> **Local run (without E2B):** run `python bot.py` directly (Option A), or for Option B run `python agentos_server.py` and expose it with an [ngrok](https://ngrok.com) tunnel before calling `setWebhook`.

## Configuration

| Variable | Required | Default | Applies to | Description |
|---|---|---|---|---|
| `TELEGRAM_TOKEN` | yes | — | both | Bot token from @BotFather. |
| `NEOSANTARA_API_KEY` | yes | — | both | Neosantara API key (read by Agno's Neosantara model). |
| `NEOSANTARA_MODEL` | no | `gemini-3-flash` | both | Neosantara model id. |
| `AGENT_INSTRUCTIONS` | no | helpful-assistant prompt | both | System instructions for the agent. |
| `ALLOWED_CHAT_IDS` | no | _(everyone)_ | `bot.py` | Comma-separated chat ids allowed to use the bot. |
| `PORT` | no | `7777` | `agentos_server.py` | Port the webhook server listens on. |
| `APP_ENV` | no | — | `agentos_server.py` | `development` skips webhook secret validation. |
| `TELEGRAM_WEBHOOK_SECRET_TOKEN` | prod | — | `agentos_server.py` | Validates the webhook secret header in production. |
| `SESSION_DB_FILE` | no | `/tmp/telegram_sessions.db` | `agentos_server.py` | SQLite file for persistent sessions. |

## Files

- `bot.py` — Option A: simple long-poll runtime (receive loop + Agno agent).
- `agentos_server.py` — Option B: Agno AgentOS Telegram interface (FastAPI webhook server).
- `build_template.py` — E2B template builder via the Python SDK (server-side build).
- `e2b.Dockerfile` — E2B template builder via the E2B CLI + Docker.
- `requirements.txt` — Python dependencies.
- `.env.example` — environment variable template.

A ready-to-run Google Colab walkthrough lives at [`cookbook/advanced/agno-telegram-e2b.ipynb`](../../cookbook/advanced/agno-telegram-e2b.ipynb).

## Customization

- **Change the model:** set `NEOSANTARA_MODEL` to any [Neosantara model](https://neosantara.xyz/models) that supports function calling.
- **Restrict access (Option A):** set `ALLOWED_CHAT_IDS` so only specific chats can use the bot.
- **Add tools:** give the Agno agent more capabilities by adding toolkits — in `build_agent()` in `bot.py`, or on the `Agent` in `agentos_server.py`.
- **Tune the AgentOS interface (Option B):** the `Telegram(...)` interface accepts options like `streaming`, `show_reasoning`, `reply_to_mentions_only`, and custom `/start` `/help` messages — see the [interface parameters](https://docs.agno.com/agent-os/interfaces/telegram/introduction#parameters).
