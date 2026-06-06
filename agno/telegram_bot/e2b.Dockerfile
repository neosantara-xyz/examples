# Agno Telegram Bot — E2B template (Docker option)
#
# An alternative to build_template.py for users who prefer the E2B CLI +
# Dockerfile workflow.
#
# Build (requires the E2B CLI + E2B_API_KEY):
#   cd examples/agno/telegram_bot
#   e2b template build --name agno-telegram --dockerfile e2b.Dockerfile
#
# Then create a sandbox and inject secrets at runtime:
#   Sandbox.create('agno-telegram', envs={'TELEGRAM_TOKEN': ..., 'NEOSANTARA_API_KEY': ...})
#   # Option A — long-poll bot:
#   sbx.commands.run('python /app/bot.py', background=True)
#   # Option B — AgentOS webhook server:
#   sbx.commands.run('APP_ENV=development python /app/agentos_server.py', background=True)

FROM python:3.12-slim

# Dependencies:
#   agno[telegram]    : Telegram Bot API helpers + the Neosantara model
#   openai            : the Neosantara model extends OpenAILike
#   fastapi[standard] : AgentOS webhook server (uvicorn, etc.)
#   sqlalchemy        : SqliteDb sessions used by agentos_server.py
#   ddgs              : DuckDuckGo web search for the Researcher (team mode)
RUN pip install --no-cache-dir "agno[telegram]" openai "fastapi[standard]" sqlalchemy ddgs

WORKDIR /app
COPY bot.py /app/bot.py
COPY agentos_server.py /app/agentos_server.py
