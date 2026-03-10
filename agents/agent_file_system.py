import json
import os
from pathlib import Path

from utils.load_env_settings import settings
from utils.model_utils import model
from utils.path_utils import project_dir

root_dir = str(project_dir)
file_system_root = settings.playwright.root_dir_name


def _parse_paths(folder_structure: str) -> list[str]:
    """Ask the LLM to convert a free-text folder tree into a JSON list of relative paths."""
    prompt = f"""
Convert the following folder/file structure into a JSON array of relative file/folder paths.
Rules:
- Paths must be relative (no leading slash).
- Every path must start with "{file_system_root}/".
- Include both directories and files exactly as described.
- Return ONLY valid JSON — no markdown, no explanation.

Example output:
["agent_test_framework/tests", "agent_test_framework/tests/__init__.py"]

Structure to convert:
{folder_structure}
"""
    response = model.invoke(prompt)
    raw = response.content.strip()
    # Strip markdown code fences if the model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _create_path(relative_path: str) -> str:
    full_path = Path(root_dir) / relative_path
    # Security: stay within root_dir
    if not full_path.resolve().is_relative_to(Path(root_dir).resolve()):
        return f"Skipped (outside sandbox): {relative_path}"

    if full_path.suffix:  # it's a file
        if full_path.exists():
            return f"Already exists (file): {relative_path}"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        return f"Created file: {relative_path}"
    else:  # it's a directory
        if full_path.exists():
            return f"Already exists (dir): {relative_path}"
        full_path.mkdir(parents=True, exist_ok=True)
        return f"Created dir: {relative_path}"


async def file_system_manager(folder_structure: str):
    paths = _parse_paths(folder_structure)
    results = [_create_path(p) for p in paths]
    summary = "\n".join(results)
    print(summary)
    return summary