from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.tracing import observe

from agents.agent_post_test_on_jira import post_test_on_jira_agent, build_jira_query
from agents.agent_generate_test_ui import TestCase, TestStep, TestCases
from config.mcp_config.jira_mcp import JIRA_MCP

def make_login_test_case() -> TestCase:
    return TestCase(
        test_id="TC-001",
        title="TC-001-Login with valid credentials",
        description="Verify that a registered user can log in with valid credentials",
        preconditions=[
            "User is registered in the system",
            "Browser is open on the login page",
        ],
        steps=[
            TestStep(step_number=1, action="Enter valid email", expected_result="Email is accepted"),
            TestStep(step_number=2, action="Enter valid password", expected_result="Password is masked"),
            TestStep(step_number=3, action="Click Login button", expected_result="User is redirected to dashboard"),
        ],
        ui_components=["email_input", "password_input", "login_button"],
        feature_area="Authentication",
        priority="High",
        source_page="https://example.com/login",
    )

def test_jira_agent_calls_correct_tool():

    tc = make_login_test_case()
    test_cases = TestCases(tests=[tc])
    query = build_jira_query(tc)

    @observe(type="agent")
    async def call(_input: str):
        return await post_test_on_jira_agent(JIRA_MCP, test_cases)

    assert_test(
        observed_callback=call,
        golden=Golden(input=query),
    )
