# from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict

# from configs.constants import EMBEDDING_MODEL_NAME, FAISS_STORE_PATH
FAISS_STORE_PATH = "/data/faiss/"

# embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
documents: List[str] = []
metadata: List[Dict] = []


def add_to_memory(text, source: str, tags: Dict = {}, **kwargs):
    embedding_model = kwargs.get("embedding_model")
    index = kwargs.get("index")
    if hasattr(text, "content"):
        text = text.content
    vector = embedding_model.encode([text])
    index.add(np.array(vector).astype("float32"))
    documents.append(text)
    metadata.append({"source": source, "tags": tags})


def retrieve_context(
    query: str, k: int = 3, embedding_model=None, **kwargs
) -> List[Dict]:
    index = kwargs.get("index")
    query_vec = embedding_model.encode([query])
    D, _ = index.search(np.array(query_vec).astype("float32"), k)
    return [
        {"text": documents[i], "metadata": metadata[i]}
        for i in _[0]
        if i < len(documents)
    ]


def save_memory(path=FAISS_STORE_PATH, **kwargs):
    index = kwargs.get("index")
    os.makedirs(path, exist_ok=True)
    faiss.write_index(index, os.path.join(path, "index.faiss"))
    with open(os.path.join(path, "meta.pkl"), "wb") as f:
        pickle.dump((documents, metadata), f)


def load_memory(path=FAISS_STORE_PATH, **kwargs):
    global documents, metadata
    # index = kwargs.get("index")
    # index = faiss.read_index(os.path.join(path, "index.faiss"))
    with open(os.path.join(path, "meta.pkl"), "rb") as f:
        documents, metadata = pickle.load(f)
