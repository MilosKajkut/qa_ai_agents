from pathlib import Path
from typing import Union

from langchain_community.document_loaders import TextLoader


class DataUtils:
    @staticmethod
    def get_file_path(file_name: Union[str, Path],
                  folder: Union[str, Path]=None) -> Path:
        file_path = Path(file_name)
        if not file_path.parent.name and not (file_path.is_file() and file_path.exists()):
            file_path = Path(folder, file_name)
        return file_path

    @staticmethod
    def read_file(file_name: Union[str, Path],
                  folder: Union[str, Path]=None) -> list:
        file_path = DataUtils.get_file_path(file_name, folder)

        match file_path.suffix:
            case ".txt":
                loader = TextLoader(file_path)
                return loader.load()
            case _:
                raise ValueError(f"Unsupported format file {file_path.suffix}")