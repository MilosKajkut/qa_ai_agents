from langchain_chroma import Chroma
from utils.load_env_settings import settings

test = settings.vector_db.collection_name

from utils.path_utils import data_dir
# TODO: Create plugin for embedding models
from config.embedded_model_config.embedding_models import HFBaaibgeM3

embedding_model = HFBaaibgeM3()

vector_store = Chroma(
    collection_name=settings.vector_db.collection_name,
    embedding_function=embedding_model.embeddings,
    persist_directory=data_dir
)
