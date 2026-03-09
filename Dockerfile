FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source code
COPY agents/ ./agents/
COPY config/ ./config/
COPY utils/ ./utils/
COPY prompts/ ./prompts/
COPY main.py ./

# pages/ and data/ are mounted as volumes at runtime
RUN mkdir -p pages data

CMD ["uv", "run", "python", "main.py"]
