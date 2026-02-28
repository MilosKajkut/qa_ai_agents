import os

from dotenv import load_dotenv
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from utils.model_utils import model
from utils.path_utils import project_dir

root_dir = str(project_dir)
load_dotenv()

file_system_root = os.getenv("ROOT_DIR_NAME")


@tool
def create_directory(directory_path: str) -> str:
    """Creates a new directory (and parent directories) within the root sandbox.
      Args:
          directory_path: The relative path of the directory to create.
    """
    full_path = os.path.join(root_dir, directory_path)
    if not os.path.commonpath([root_dir, full_path]) == root_dir:
        return "Error: specific path is outside the sandbox root."

    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Successfully created directory: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {e}"


def file_system_manager(folder_structure: str):
    toolkit = FileManagementToolkit(
        root_dir=root_dir,
        selected_tools=["read_file", "write_file", "list_directory", "file_search"]
    )

    tools = toolkit.get_tools() + [create_directory]

    agent = create_react_agent(model, tools)

    prompt = (
        f"""
        Your job is to create folder/file structure following this pattern: {folder_structure}.
        Follow rules:
        
        1. If folder/file already exists, do not create folder/file.
        2. If folder/file does not exist, create folder/file.
        3. Create folders/files in {file_system_root} path.
        4. If file have extension .py, create python file.
        
        """
    )

    result = agent.invoke(
        {"messages": [("user", prompt)]},
    )

    last_message = result["messages"][-1]
    print(last_message)

    return last_message