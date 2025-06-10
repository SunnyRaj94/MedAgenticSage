# from langchain.vectorstores import Chroma, FAISS
from langchain_community.vectorstores import Chroma, FAISS

# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from abc import ABC, abstractmethod
import os

"""
💡 Vector Store Options (RAG-friendly)
Store	|| Persistence	|| Performance	|| Comments
Chroma	|| Yes	        || Fast	        || Easy to use, great for dev.
FAISS	|| No (in-mem)	|| Very fast	|| Lightweight, local only.
Qdrant	|| Yes	        || High	        || Suitable for prod use.
Weaviate||	Yes	        || High	        || Advanced, good ecosystem.
"""


class VectorStoreBase(ABC):
    @abstractmethod
    def add_documents(self, docs: list[str], metadata: list[dict] = None):
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 3) -> list[str]:
        pass

    @abstractmethod
    def as_retriever(self, k: int = 3):
        pass


class ChromaVectorStore(VectorStoreBase):
    def __init__(self, persist_dir: str, embedding_model: str = "all-MiniLM-L6-v2"):
        if not persist_dir:
            raise ValueError("persist_dir must be a valid path.")
        os.makedirs(persist_dir, exist_ok=True)
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.store = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
        )

    def add_documents(self, docs, metadata=None):
        self.store.add_texts(docs, metadatas=metadata)

    def similarity_search(self, query, k=3):
        return self.store.similarity_search(query, k=k)

    def as_retriever(self, k=3):
        return self.store.as_retriever(search_kwargs={"k": k})


class FAISSVectorStore(VectorStoreBase):
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.store = FAISS.from_texts([], self.embeddings)

    def add_documents(self, docs, metadata=None):
        new_store = FAISS.from_texts(docs, self.embeddings)
        self.store.merge_from(new_store)

    def similarity_search(self, query, k=3):
        return self.store.similarity_search(query, k=k)

    def as_retriever(self, k=3):
        return self.store.as_retriever(search_kwargs={"k": k})


def get_vector_store(store_type: str = "chroma", **kwargs) -> VectorStoreBase:
    if store_type == "chroma":
        return ChromaVectorStore(**kwargs)
    elif store_type == "faiss":
        return FAISSVectorStore(**kwargs)
    else:
        raise ValueError(f"Unsupported store type: {store_type}")


def get_vector_retriever(store_type="chroma", k=3, **kwargs):
    store = get_vector_store(store_type=store_type, **kwargs)
    return store


def get_embeddings_model(model_name=None):
    from sentence_transformers import SentenceTransformer

    model_name = (
        "sentence-transformers/all-MiniLM-L6-v2" if not model_name else model_name
    )
    global_embedding_model_for_memory = SentenceTransformer(model_name)
    return global_embedding_model_for_memory
