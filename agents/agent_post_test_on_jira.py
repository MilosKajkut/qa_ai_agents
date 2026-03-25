import asyncio
import json
import os

from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.tracing import update_current_span
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agents.agent_generate_test_ui import TestCases, TestCase
from utils.extract_msg.ai_message import get_tool_call_from_ai_message
from utils.model_utils import model

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field
from deepeval.tracing import observe

JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "KAN")


class JiraTestCase(BaseModel):
    key: str = Field(description="Test case Key like KAN-204")
    title: str = Field(description="Brief test title")


def extract_tool_message(message_content: str) -> dict:
    payload = json.loads(message_content)
    issue = payload.get("issue")
    key = issue.get("key")
    title = issue.get("summary")

    return {"key": key, "title": title}


def extract_jira_results(messages: list,
                         message_type: type[HumanMessage | AIMessage | ToolMessage],
                         extraction_fun: callable,
                         base_model: type[BaseModel]) -> BaseModel | JiraTestCase:
    matched_messages = [msg for msg in messages if isinstance(msg, message_type)]

    if not matched_messages:
        raise ValueError(f"No message of type {message_type.__name__} found in {len(messages)} messages")

    last_message = matched_messages[-1]
    extracted_values = extraction_fun(last_message.content)
    return base_model(**extracted_values)


def build_jira_query(tc: TestCase, project_key: str = JIRA_PROJECT_KEY) -> str:
    steps_formatted = "\n".join(
        f"{step.step_number}. {step.action} → Expected: {step.expected_result}"
        for step in tc.steps
    )
    preconditions = "\n".join(f"- {p}" for p in tc.preconditions)

    return f"""
            CONTEXT:
                Creating Issue based on provided Test Cases for project {project_key}.
                Issue should follow rules in format and writing.

            TASK:
                Your task is to create Issue in Jira for Test Cases.
                Create Jira issue in project {project_key} with the following exact values.
                Do not infer, summarize, or modify any field — use the values exactly as provided.
            RULES:

                ISSUE TITLE:
                {tc.title}

                In Description of Issue put following:

                                PRECONDITIONS:
                                {preconditions}

                                TEST STEPS:
                                {steps_formatted}

                                SOURCE PAGE: {tc.source_page}

            Do not ask for confirmation.
            """

@observe(type="agent", metrics=[ToolCorrectnessMetric()])
async def post_test_on_jira_agent(mcp_config: dict, test_cases: TestCases, post_retries=2) -> (list, TestCases):
    client = MultiServerMCPClient(mcp_config["config"])

    async with client.session(mcp_config["mcp_name"]) as session:
        mcp_tools = await load_mcp_tools(session)
        agent = create_react_agent(model, mcp_tools)

        results = []
        for test_case in test_cases.tests:
            for attempt in range(post_retries + 1):
                query = build_jira_query(test_case)
                try:
                    # get final result of execution
                    result = await agent.ainvoke({"messages": [("user", query)]})
                except Exception as e:
                    print(f"[warn] Attempt {attempt + 1} failed for '{test_case.title}': {e}")
                    if attempt == post_retries:
                        print(f"Test Case {test_case.test_id}: {test_case.title} could not be posted on Jira.")
                    else:
                        await asyncio.sleep(2 ** attempt)

                # create LLMTestCase for evaluation
                used_tools = get_tool_call_from_ai_message(result)
                llm_test_case = LLMTestCase(
                    input=str(test_cases),
                    actual_output="We offer a 30-day full refund at no extra cost.",
                    # Replace this with the tools that was actually used by your LLM agent
                    tools_called=[ToolCall(name=tool["name"]) for tool in used_tools],
                    expected_tools=[ToolCall(name="jira_create_issue")],
                )
                update_current_span(test_case=llm_test_case)

                # get created jira test case
                jira_test_case: JiraTestCase = extract_jira_results(result["messages"],
                                                                    ToolMessage,
                                                                    extract_tool_message,
                                                                    JiraTestCase)
                test_case.test_id = jira_test_case.key
                results.append(test_case.test_id)
                print(f"Test Case {test_case.test_id}: {test_case.title} successfully posted on Jira.")
                break

        return results, test_cases