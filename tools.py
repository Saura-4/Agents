from google.genai import types

from clients import tavily_client, client

import math
import os
import json

def calculator(expression: str):
    return eval(expression)


calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="calculator",
            description="Calculate a mathematical expression.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "expression": types.Schema(
                        type="STRING",
                        description="The mathematical expression to calculate."
                    )
                },
                required=["expression"],
            ),
        )
    ]
)


notes = []


def save_notes(note: str):
    notes.append(note)
    return "Notes save successfully."


def retrieve_notes():
    return notes


save_note_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="save_notes",
            description="for saving notes",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "note": types.Schema(
                        type="STRING",
                        description="save note"
                    )
                },
                required=["note"],
            ),
        )
    ]
)

retrieve_notes_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_notes",
            description="Retrieve Notes",
            parameters=types.Schema(
                type="OBJECT"
            ),
        )
    ]
)


def search(query: str):
    print("Search query:", repr(query))

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5,
    )

    results = []

    for i, result in enumerate(response["results"], start=1):
        results.append({
            "id": i,
            "title": result["title"],
            "url": result["url"],
            "content": result["content"],
        })

    return results


search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search",
            description="Search the web for current and relevant information.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(
                        type="STRING",
                        description="The web search query."
                    )
                },
                required=["query"],
            ),
        )
    ]
)


MEMORY_FILE  = "memory.json"



def load_memories():
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: str):
    memories = load_memories()
    memories.append(memory)

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=2)

    return "Memory saved successfully."

save_memory_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="save_memory",
            description="Save information to long-term memory.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "memory": types.Schema(
                        type="STRING",
                        description="Information that should be remembered."
                    )
                },
                required=["memory"],
            ),
        )
    ]
)


MEMORY_FILE_WITH_METADATA = "memory_with_metadata.json"

def load_memories_with_metadata():
    if not os.path.exists(MEMORY_FILE_WITH_METADATA):
        return []

    with open(MEMORY_FILE_WITH_METADATA, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_with_metadata(memory: str, category: str):
    memories = load_memories_with_metadata()
    memories.append(
        {
            "memory": memory,
            "category": category
        }
    )

    with open(MEMORY_FILE_WITH_METADATA, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=2)

    return "Memory saved successfully."

save_memory_with_metadata_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="save_memory_with_metadata",
            description="Save information to long-term memory.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "memory": types.Schema(
                        type="STRING",
                        description="Information that should be remembered."
                    ),
                    "category": types.Schema(
                        type="STRING",
                        description="Category of the memory"
                    )
                },
                required=["memory","category"],
            ),
        )
    ]
)

def retrieve_memories_by_category(category: str):
    memories = load_memories_with_metadata()

    return [
        memory
        for memory in memories
        if memory["category"] == category
    ]


retrieve_memory_with_metadata_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_memories_by_category",
            description="retrieve_memories_by_category",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "category": types.Schema(
                        type="STRING",
                        description="Category of the memory"
                    )
                },
                required=["category"],
            ),
        )
    ]
)


def retrieve_memories():
    return load_memories()

retrieve_memories_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_memories",
            description="Retrieve all stored long-term memories.",
            parameters=types.Schema(
                type="OBJECT"
            ),
        )
    ]
)


def retrieve_last_n_memories(n: int = 5):
    memories = load_memories()
    return memories[-n:]

retrieve_last_n_memories_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_last_n_memories",
            description="Retrieve the most recent N long-term memories.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "n": types.Schema(
                        type="INTEGER",
                        description="Number of recent memories to retrieve."
                    )
                },
                required=["n"],
            ),
        )
    ]
)



def retrieve_memories_by_keyword(keyword: str):
    memories = load_memories()

    keyword = keyword.lower()

    return [
        memory
        for memory in memories
        if keyword in memory["memory"].lower()
    ]




EMBEDDING_MODEL = "gemini-embedding-001"
MEMORY_EMBEDDINGS_FILE = "memory_embeddings.json"


def embed_text(text: str, task_type: str):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type
        ),
    )

    return response.embeddings[0].values

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def load_memory_embeddings():
    if not os.path.exists(MEMORY_EMBEDDINGS_FILE):
        return {}

    with open(MEMORY_EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory_embeddings(embeddings):
    with open(MEMORY_EMBEDDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings, f)

def ensure_memory_embeddings():
    memories = load_memories()
    embeddings = load_memory_embeddings()

    changed = False

    for index, memory in enumerate(memories):

        key = str(index)

        if key not in embeddings:
            embeddings[key] = embed_text(
                memory,
                "RETRIEVAL_DOCUMENT"
            )
            
            changed = True

    if changed:
        save_memory_embeddings(embeddings)

    return memories, embeddings


def retrieve_memories_vector(
    query: str,
    top_k: int = 3,
    threshold: float = 0.75,
    ):
    memories, embeddings = ensure_memory_embeddings()

    if not memories:
        return []

    query_embedding = embed_text(
        query,
        "RETRIEVAL_QUERY"
    )

    scored_memories = []

    for index, memory in enumerate(memories):

        embedding = embeddings[str(index)]

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        scored_memories.append({
            "memory": memory,
            "similarity": score,
        })

    scored_memories.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    results = [
        item
        for item in scored_memories
        if item["similarity"] >= threshold
    ]

    return results[:top_k]


retrieve_vector_memory_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="retrieve_memories_vector",
            description=(
                "Retrieve long-term memories using semantic vector "
                "similarity."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(
                        type="STRING",
                        description=(
                            "The information to search for in long-term memory."
                        ),
                    )
                },
                required=["query"],
            ),
        )
    ]
)



import chromadb

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

memory_collection = chroma_client.get_or_create_collection(
    name="memories"
)


import chromadb

MEMORY_CHROMA_FILE = "memory_chroma.json"

chroma_client = chromadb.PersistentClient(
    path="./chroma_memory"
)

chroma_collection = chroma_client.get_or_create_collection(
    name="memory_chroma"
)


def load_chroma_memories():
    with open(MEMORY_CHROMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_chroma_memories():
    memories = load_chroma_memories()

    existing = chroma_collection.count()

    if existing == len(memories):
        return memories

    for index, memory in enumerate(memories):

        memory_id = str(index)

        result = chroma_collection.get(
            ids=[memory_id]
        )

        if not result["ids"]:
            embedding = embed_text(
                memory,
                "RETRIEVAL_DOCUMENT"
            )

            chroma_collection.add(
                ids=[memory_id],
                documents=[memory],
                embeddings=[embedding]
            )

    return memories


def retrieve_memories_chroma(
    query: str,
    top_k: int = 3,
):
    ensure_chroma_memories()

    query_embedding = embed_text(
        query,
        "RETRIEVAL_QUERY"
    )

    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    memories = results["documents"][0]
    distances = results["distances"][0]

    return [
        {
            "memory": memory,
            "distance": distance,
        }
        for memory, distance in zip(memories, distances)
    ]






ALL_TOOLS = [calculator_tool, save_note_tool, retrieve_notes_tool, save_memory_tool, retrieve_vector_memory_tool,]