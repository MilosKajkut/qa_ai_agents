from langchain_core.messages import AIMessage


def get_tool_call_from_ai_message(messages: dict) -> list:
    ai_messages: list[AIMessage] = list()
    tools = list()

    for message in messages["messages"]:
        if isinstance(message, AIMessage):
            ai_messages.append(message)

    if not len(ai_messages):
        return tools

    for ai_message in ai_messages:
        tools_call = ai_message.tool_calls
        for tool in tools_call:
            tools.append({'name': tool['name'], 'args': tool['args']})

    return tools