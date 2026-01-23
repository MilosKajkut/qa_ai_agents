from joblib.externals.loky.backend.queues import Queue

from agents.agent_post_test_on_jira import run_confluence_agent
from utils.data_utils import DataUtils
from utils.path_utils import data_dir
from config.mcp_config.confluence_mcp import CONFLUENCE_MCP
from config.mcp_config.jira_mcp import JIRA_MCP

import asyncio

REQUIREMENTS = "requirements.txt"
requirements = DataUtils.read_file(REQUIREMENTS, data_dir)

# query = (
#             f"""
#             ROLE:
#             You are Expert Software Test Engineer with great expirience in testing, writing test case,
#             writing Test Plans.
#
#             CONTEXT:
#             You are testing application which URL is at https://testers.ai. You should visit this site and create Tests
#             Plan based on that web page.
#
#             TASK:
#             Your task is to create Test Plan based on requirements. Test Plan should be structured based on the best
#             practices and testing principals. After you create Test Plan you should Create a new page in the Confluence
#             space with key 'TEST' (Testing/QA Team). The title should be 'Test Plan for Dummy app'.
#             The Content of the page should be previous created Test Plan formated to be easy to analys and read.
#
#             RULES:
#             1. Create robust Test Plan which will cover all aspects of Testing procedures and testing app.
#
#             """
#         )

query = (
    """
    Create Issue named TestIssue for project KAN?
    """
)

message = asyncio.run(run_confluence_agent(JIRA_MCP, query))

print(message)


