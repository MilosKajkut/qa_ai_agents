# QA AI Agents

AI-powered agents for QA automation — generates test cases from UI screenshots and posts them to Jira.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

## Setup

### 1. Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and install dependencies

```bash
git clone <repo-url>
cd qa_ai_agents

# Create virtual environment and install all dependencies from uv.lock
uv sync
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `ANTHROPIC_API_KEY` — Anthropic Claude API key
- `OPENAI_API_KEY` — OpenAI API key
- `JIRA_URL` — Your Jira instance URL
- `JIRA_EMAIL` — Jira account email
- `JIRA_API_TOKEN` — Jira API token

### 4. Run

```bash
uv run python main.py
```

## Project Structure

```
qa_ai_agents/
├── agents/                  # AI agent definitions
│   ├── agent_generate_test_ui.py   # Generates test cases from screenshots
│   ├── agent_post_test_on_jira.py  # Posts test cases to Jira
│   └── agent_file_system.py        # File system management agent
├── config/
│   ├── embedded_model_config/      # Embedding model configuration
│   └── mcp_config/                 # MCP (Jira) configuration
├── utils/                   # Shared utilities
│   ├── chroma_setup.py      # ChromaDB vector store setup
│   ├── model_utils.py       # LLM model initialization
│   ├── load_env_settings.py # Environment settings
│   ├── path_utils.py        # Path helpers
│   └── tools.py             # Shared tools
├── pages/                   # UI screenshots for test generation
├── data/                    # ChromaDB persistent storage
├── main.py                  # Entry point and LangGraph workflow
├── pyproject.toml           # Project metadata and dependencies
└── uv.lock                  # Locked dependency versions
```