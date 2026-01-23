import asyncio
from pathlib import Path

from config.mcp_config.jira_mcp import JIRA_MCP
from utils.path_utils import pages_dir
from utils.model_utils import model
from agents.agent_generate_test_ui import generate_manual_test_based_on_image
from agents.agent_post_test_on_jira import post_test_on_jira_agent

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, add_messages

page_image = Path(pages_dir, "testers-ai-testing-wcag_a","testers-ai-testing-wcag_a_agents_tasks.JPG")


class AgentState(TypedDict):
    # Using add_messages allows the graph to append history automatically
    messages: Annotated[list[BaseMessage], add_messages]


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


workflow = StateGraph(AgentState)
workflow.add_node("manual_test_agent", manual_test_agent)
workflow.add_node("post_test_on_jira", post_test_on_jira)
workflow.add_edge(START, "manual_test_agent")
workflow.add_edge("manual_test_agent", "post_test_on_jira")
workflow.add_edge("post_test_on_jira", END)
app = workflow.compile()


msg = "From this image, act as Senior Test Developer and generate test cases which will cover 100% tests for web page shown in the image"
input_payload = {"messages": [HumanMessage(content=msg)]}

for chunk in app.stream(input_payload):
    for message in chunk['manual_test_agent']['messages']:
        print(message.content)
        print("=================")
