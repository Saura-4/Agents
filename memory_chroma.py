import json
import os

import chromadb

from memory import load_memories


MEMORY_CHROMA_FILE = "memory_chroma.json"
CHROMA_PATH = "./chroma_db"


chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

memory_collection = chroma_client.get_or_create_collection(
    name="memories"
)


def load_chroma_memory_data():
    if not os.path.exists(MEMORY_CHROMA_FILE):
        return {}

    with open(MEMORY_CHROMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chroma_memory_data(data):
    with open(MEMORY_CHROMA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def embed_memory(memory: str):
    from tools import embed_text

    return embed_text(
        memory,
        "RETRIEVAL_DOCUMENT"
    )


def save_memory_chroma(memory: str):
    data = load_chroma_memory_data()

    memory_id = str(len(data))

    embedding = embed_memory(memory)

    memory_collection.add(
        ids=[memory_id],
        documents=[memory],
        embeddings=[embedding],
    )

    data[memory_id] = {
        "memory": memory,
        "chroma_id": memory_id,
    }

    save_chroma_memory_data(data)


def initialize_chroma_memories():
    memories = load_memories()
    data = load_chroma_memory_data()

    for index, memory in enumerate(memories):

        memory_id = str(index)

        if memory_id in data:
            continue

        save_memory_chroma(memory)


def retrieve_memories_chroma(
    query: str,
    top_k: int = 3,
):
    from tools import embed_text

    query_embedding = embed_text(
        query,
        "RETRIEVAL_QUERY"
    )

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    memories = results["documents"][0]

    return memories