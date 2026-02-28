import asyncio
from pathlib import Path

from config.mcp_config.jira_mcp import JIRA_MCP
from utils.chroma_setup import vector_store
from utils.path_utils import pages_dir
from utils.model_utils import model
from agents.agent_generate_test_ui import generate_manual_test_based_on_image, TestCases, TestCase
from agents.agent_post_test_on_jira import post_test_on_jira_agent, JiraTestCase
from agents.agent_file_system import file_system_manager

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.documents import Document

page_images = Path(pages_dir, "testers-ai-testing-wcag_a")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    framework_structure: str
    test_cases: TestCases
    jira_test_case_ids: list[JiraTestCase]


async def manual_test_agent(state: AgentState):
    latest_user_message = state["messages"][-1]
    user_prompt_text = latest_user_message.content

    jpg_files = list(page_images.glob("*.JPG"))
    if not jpg_files:
        raise FileNotFoundError(f"No images found in {page_images}")

    all_test_cases: list[TestCase] = []

    async def process_image(page_image: Path, index: int):
        human_msg, sys_msg = generate_manual_test_based_on_image(user_prompt_text, page_image)
        structured_model = model.with_structured_output(TestCases)
        messages_payload = [sys_msg, human_msg]

        test_cases: TestCases = await structured_model.ainvoke(messages_payload)

        for tc in test_cases.tests:
            tc.source_page = page_image.stem

        return test_cases.tests

    results = await asyncio.gather(
        *[process_image(img, i) for i, img in enumerate(jpg_files)],
        return_exceptions=True
    )

    for result in results:
        if isinstance(result, Exception):
            print(f"[warn] Image processing failed: {result}")
            continue
        for tc in result:
            all_test_cases.append(tc)

    if not all_test_cases:
        raise RuntimeError("All image processing failed — no test cases generated")

    return {"test_cases": TestCases(tests=all_test_cases)}


def put_test_in_vector_db(state: AgentState):
    test_cases: TestCases = state.get("test_cases")
    if not test_cases or not test_cases.tests:
        print("[warn] No test cases to store in vector DB")
        return {}

    docs = [
        Document(
            page_content=tc.model_dump_json(),
            metadata={"test_id": tc.test_id, "source_page": tc.source_page}
        )
        for tc in test_cases.tests
    ]
    vector_store.add_documents(documents=docs)

    query = "Which tests test Voice Assistant Agent information?"
    results = vector_store.similarity_search(query)
    print(results)
    return {}


async def post_test_on_jira(state: AgentState):
    tests = state.get("test_cases", None)

    jira_test_case_ids, updated_tests = await post_test_on_jira_agent(JIRA_MCP, tests)

    return {"test_cases": updated_tests, "jira_test_case_ids": jira_test_case_ids}


def generate_folder_structure_framework(state: AgentState):
    tests = state.get("test_cases", None)

    prompt = \
        f"""
        For test cases from list {tests}, create framework folders/files structure following Page Object 
        Model pattern for Playwright Python. Include also folder/files which are related to utils, config, helpers etc.
        Root folder should be named "agent_test_framework" 
        Provide only folder structure and nothing else.
        """

    response = model.invoke(prompt)

    return {"framework_structure": response.content}


def create_file_system_structure(state: AgentState):
    framework_system_file = state.get("framework_structure", None)
    if framework_system_file is None:
        raise Exception("There is no information about Framework structure.")

    response = file_system_manager(framework_system_file)

    return {"messages": [response]}


### SETUP WORKFLOW ###
workflow = StateGraph(AgentState)

### SETUP NODES ###
workflow.add_node("manual_test_agent", manual_test_agent)
workflow.add_node("post_test_on_jira", post_test_on_jira)
workflow.add_node("create_file_system_structure", create_file_system_structure)
workflow.add_node("generate_folder_structure_framework", generate_folder_structure_framework)
workflow.add_node("put_test_in_vector_db", put_test_in_vector_db)

### SETUP EDGES ###
workflow.add_edge(START, "manual_test_agent")
workflow.add_edge("manual_test_agent", "post_test_on_jira")
workflow.add_edge("manual_test_agent", "generate_folder_structure_framework")
workflow.add_edge("post_test_on_jira", "put_test_in_vector_db")
workflow.add_edge("put_test_in_vector_db", END)
workflow.add_edge("generate_folder_structure_framework", "create_file_system_structure")
workflow.add_edge("create_file_system_structure", END)

### START APP ###
app = workflow.compile()

msg = ("From this image, "
       "act as Senior Test Developer and generate test cases which "
       "will cover 100% tests for web page shown in the image")


async def main():
    input_payload = {"messages": [HumanMessage(content=msg)]}
    async for chunk in app.astream(input_payload):
        if "generate_folder_structure_framework" in chunk:
            fw_structure = chunk["generate_folder_structure_framework"]["framework_structure"]
            print(fw_structure)
            print("=================")


asyncio.run(main())
