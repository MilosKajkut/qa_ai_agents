from utils.model_utils import model

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def post_test_on_jira_agent(mcp_config: dict, test_cases: str) -> str:
    query = (
        f"""
                ROLE:
                You are Jira exper for creating Issues in  Jira.

                CONTEXT:
                Creating Issue based on provided Test Cases for project for project KAN. Issue should follow rules in format and writing.

                TASK:
                Your task is to create Issue in Jira for Test Cases. Test Cases are provided here: {test_cases}.
                Each Test Case should have corresponding Issue in Jira.

                RULES:
                1. Issue Title should be the same as Test Case title.
                
                In Description of Issue put following: 
                    2. Description should be the same as Test Case description.
                    3. Precondition should be the same as Test Case precondition.
                    4. Test Steps should be numerated.
                    5. Steps should be the same as Test Case Steps.
                    6. Test Step format should be:
                            <Step Number>. <Test Step>  - <Test Step Expected Result
                """
    )

    client = MultiServerMCPClient(mcp_config["config"])
    async with client.session(mcp_config["mcp_name"]) as session:
        mcp_tools = await load_mcp_tools(session)

        agent = create_react_agent(model, mcp_tools)

        print(f"🤖 Agent acting on: '{query}'")

        result = await agent.ainvoke({"messages": [("user", query)]})

        last_message = result["messages"][-1]
        print(last_message)

        return last_message
