from config.mcp_config.mcp_config import configure_atlassian_mcp

JIRA_MCP = configure_atlassian_mcp("JIRA_URL",
                                   "JIRA_USERNAME",
                                   "JIRA_API_TOKEN")