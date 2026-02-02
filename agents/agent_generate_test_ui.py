from langchain_core.messages import HumanMessage, SystemMessage

from utils.tools import covert_image_to_base64

SYSTEM_TEST_ENG_MESSAGE = SystemMessage("""
            You are Senior Test Engineer with great experience in writing manual test cases. 
            You task is to write manual test case for web page following the best practices and standards. 
            For Testing, follow ISTQB practices for testing technices.
            Each test case should have title like TC-<ID>-<Name of Test case>, 
            Description where will be explain test case objectives,
            Precondition section, where will be explained precondition for each test case. 
            Test steps should be numerated and detailed, also each test step should have expected results.
            Provide only test, nothing else.
            """)


def generate_manual_test_based_on_image(text_query, path_to_image) -> tuple[HumanMessage, SystemMessage]:
    # covert image to base64
    image_base64 = covert_image_to_base64(path_to_image)

    human_message = HumanMessage(
        content=[
            {"type": "text", "text": text_query},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "low"
                }
            },
        ]
    )

    return human_message, SYSTEM_TEST_ENG_MESSAGE
