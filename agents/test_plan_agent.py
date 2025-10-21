from utils.data_utils import DataUtils
from utils.path_utils import data_dir
from utils.model_utils import model
from prompts.requirements_prompts import create_tests_template

from langchain.prompts import ChatPromptTemplate


REQUIREMENTS = "requirements.txt"

requirements = DataUtils.read_file(REQUIREMENTS, data_dir)
prompt_template = ChatPromptTemplate.from_template(create_tests_template)

actual_prompt = prompt_template.invoke({"requirements": requirements})


results = model.invoke(actual_prompt)
print(results)



