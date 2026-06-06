"""
Build the Agno + Telegram E2B template (server-side build, no local Docker).

This packages two ways to run the bot into one reusable E2B sandbox template:

  - bot.py            Minimal long-poll loop (mirrors E2B's OpenClaw Telegram
                      example). Simplest to run; no public URL needed.
  - agentos_server.py Agno's official AgentOS Telegram interface (FastAPI
                      webhooks): streaming, sessions, /commands, media, groups.
                      Needs a public URL + Telegram setWebhook.

Both use the Neosantara model provider.

Usage (from this folder):
    pip install e2b
    export E2B_API_KEY=...           # from https://e2b.dev/dashboard
    python build_template.py

Then create a sandbox and pick a runtime:

    from e2b import Sandbox

    sbx = Sandbox.create(
        "agno-telegram",
        envs={
            "TELEGRAM_TOKEN": "<bot-token-from-BotFather>",
            "NEOSANTARA_API_KEY": "<your-neosantara-key>",
        },
        timeout=3600,
    )

    # Option A — simple long-poll bot:
    sbx.commands.run("python /app/bot.py", background=True)

    # Option B — AgentOS webhook server (then register the webhook):
    # sbx.commands.run("APP_ENV=development python /app/agentos_server.py", background=True)
"""

import os
import sys

from e2b import Template, default_build_logger

NAME = "agno-telegram"

# Ubuntu base + Python. Dependencies:
#   - agno[telegram]    : Telegram Bot API helpers + the Neosantara model
#   - openai            : the Neosantara model extends OpenAILike
#   - fastapi[standard] : AgentOS webhook server (uvicorn, etc.)
#   - sqlalchemy        : SqliteDb sessions used by agentos_server.py
#   - ddgs              : DuckDuckGo web search for the Researcher (team mode)
template = (
    Template()
    .from_ubuntu_image("22.04")
    .apt_install(["python3", "python3-pip", "curl"])
    .pip_install(["agno[telegram]", "openai", "fastapi[standard]", "sqlalchemy", "ddgs"])
    .set_workdir("/app")
    .copy("bot.py", "/app/bot.py")
    .copy("agentos_server.py", "/app/agentos_server.py")
)


def main() -> None:
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    print(f'Building E2B template "{NAME}"...')
    info = Template.build(
        template,
        alias=NAME,
        cpu_count=2,
        memory_mb=4096,
        on_build_logs=default_build_logger(),
    )
    print("\nBuild complete:", info)
    print(
        f"\nCreate a sandbox with:  Sandbox.create('{NAME}', "
        "envs={'TELEGRAM_TOKEN': ..., 'NEOSANTARA_API_KEY': ...})"
    )


if __name__ == "__main__":
    main()
