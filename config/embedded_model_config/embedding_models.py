from langchain_huggingface import HuggingFaceEmbeddings


class HFBaaibgeM3:

    def __init__(self):
        self.model_name = "BAAI/bge-m3"
        self.encode_kwargs = {'normalize_embeddings': True}
        self.model_kwargs = {'device': 'cpu'}

        # create embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            encode_kwargs=self.encode_kwargs,
            model_kwargs=self.model_kwargs
        )
