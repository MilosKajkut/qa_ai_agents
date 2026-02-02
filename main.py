import asyncio
from pathlib import Path

from config.mcp_config.jira_mcp import JIRA_MCP
from utils.path_utils import pages_dir
from utils.model_utils import model
from agents.agent_generate_test_ui import generate_manual_test_based_on_image
from agents.agent_post_test_on_jira import post_test_on_jira_agent
from agents.agent_file_system import file_system_manager

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, add_messages

page_image = Path(pages_dir, "testers-ai-testing-wcag_a","testers-ai-testing-wcag_a_agents_tasks.JPG")


class AgentState(TypedDict):
    # Using add_messages allows the graph to append history automatically
    messages: Annotated[list[BaseMessage], add_messages]

    framework_structure: str


def manual_test_agent(state: AgentState):
    latest_user_message = state["messages"][-1]
    user_prompt_text = latest_user_message.content

    human_msg, sys_msg = generate_manual_test_based_on_image(user_prompt_text, page_image)
    messages_payload = [sys_msg, human_msg]

    messages_as_dicts = [msg.model_dump() for msg in messages_payload]
    response = model.invoke(messages_as_dicts)
    return {"messages": [response]}


def post_test_on_jira(state: AgentState):
    latest_user_message = state["messages"][-1]
    user_prompt_text = latest_user_message.content

    response = asyncio.run(post_test_on_jira_agent(JIRA_MCP, user_prompt_text))

    return {"messages": [response]}


def generate_folder_structure_framework(state: AgentState):
    latest_user_message = state["messages"][-1]
    user_prompt_text = latest_user_message.content

    prompt =\
        f"""
        For test cases from list {user_prompt_text}, create framework folders/files structure following Page Object 
        Model pattern for Playwright Python. Include also folder/files which are related to utils, config, helpers etc.
        Root folder should be named "agent_test_framework" 
        Provide only folder structure and nothing else.
        """

    response = model.invoke(prompt)

    return {"messages": [response], "framework_structure": response.content}


def create_file_system_structure(state: AgentState):
    framework_system_file = state.get("framework_structure", None)
    if framework_system_file is None:
        raise Exception("There is no information about Framework structure.")

    response = file_system_manager(framework_system_file)

    return {"messages": [response]}


workflow = StateGraph(AgentState)
workflow.add_node("manual_test_agent", manual_test_agent)
workflow.add_node("post_test_on_jira", post_test_on_jira)
workflow.add_node("create_file_system_structure", create_file_system_structure)
workflow.add_node("generate_folder_structure_framework", generate_folder_structure_framework)
workflow.add_edge(START, "manual_test_agent")
workflow.add_edge("manual_test_agent", "post_test_on_jira")
workflow.add_edge("manual_test_agent", "generate_folder_structure_framework")
workflow.add_edge("post_test_on_jira", END)
workflow.add_edge("generate_folder_structure_framework", "create_file_system_structure")
workflow.add_edge("create_file_system_structure", END)
app = workflow.compile()


msg = "From this image, act as Senior Test Developer and generate test cases which will cover 100% tests for web page shown in the image"
input_payload = {"messages": [HumanMessage(content=msg)]}

for chunk in app.stream(input_payload):
    if "generate_folder_structure_framework" in chunk.keys():
        for message in chunk['generate_folder_structure_framework']['messages']:
            print(message.content)
            print("=================")
