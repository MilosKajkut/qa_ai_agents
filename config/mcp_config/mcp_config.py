import os

from dotenv import load_dotenv

load_dotenv()


# Atlassian MPC Configuration
def configure_atlassian_mcp(url: str, user_name: str, api_token: str):
    url_value = os.getenv(f"{url}")
    user_name_value = os.getenv(f"{user_name}")
    api_token_value = os.getenv(f"{api_token}")

    return {
        "mcp_name": "atlassian",
        "config": {
            "atlassian": {
                "transport": "stdio",
                "command": "docker",
                "args": [
                    "run",
                    "-i",  # Interactive mode is required for stdio
                    "--rm",  # Remove container after exit
                    "-e", f"{url}={url_value}",
                    "-e", f"{user_name}={user_name_value}",
                    "-e", f"{api_token}={api_token_value}",
                    "ghcr.io/sooperset/mcp-atlassian:latest"
                ],
            }
        }
    }
