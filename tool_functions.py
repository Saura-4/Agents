"""Tool implementations and the single dispatcher used by the agent."""

_notes: list[str] = []


def save_note(note: str) -> str:
    _notes.append(note)
    return "Note saved successfully."


def retrieve_notes() -> list[str]:
    return list(_notes)


def save_memory(memory: str) -> dict:
    """Persist a memory, then immediately update both retrieval indexes."""
    from memory.chroma_search import index_memory
    from memory.embeddings import store_embedding
    from memory.storage import save_memory as save_memory_record

    record = save_memory_record(memory)
    embedding = store_embedding(record["id"], record["memory"])
    index_memory(record, embedding)
    from memory.bm25_index import update_bm25_index
    update_bm25_index(record)
    return {"message": "Memory saved successfully.", "memory": record}


def execute_tool(name: str, arguments: dict | None = None):
    """Execute one tool and turn expected failures into model-readable output."""
    arguments = arguments or {}
    handlers = {
        "search": lambda: _search(arguments["query"]),
        "save_note": lambda: save_note(arguments["note"]),
        "retrieve_notes": retrieve_notes,
        "save_memory": lambda: save_memory(arguments["memory"]),
        "retrieve_memories": _load_memories,
        "retrieve_last_n_memories": lambda: _get_last_memories(arguments.get("n", 5)),
        "retrieve_memories_vector": lambda: _retrieve_vector(arguments["query"], arguments.get("top_k", 3)),
        "retrieve_memories_chroma": lambda: _retrieve_chroma(arguments["query"], arguments.get("top_k", 3)),
        "retrieve_memories_bm25": lambda: _retrieve_bm25(arguments["query"], arguments.get("top_k", 3)),
        "retrieve_memories_hybrid": lambda: _retrieve_hybrid(arguments["query"]),
    }
    handler = handlers.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler()
    except Exception as error:
        return {"error": f"Tool error: {type(error).__name__}: {error}"}


def _search(query: str):
    from search import search_web
    return search_web(query)


def _load_memories():
    from memory.storage import load_memories
    return load_memories()


def _get_last_memories(n: int):
    from memory.storage import get_last_memories
    return get_last_memories(n)


def _retrieve_vector(query: str, top_k: int):
    from memory.vector_search import retrieve_memories_vector
    return retrieve_memories_vector(query, top_k)


def _retrieve_chroma(query: str, top_k: int):
    from memory.chroma_search import retrieve_memories_chroma
    return retrieve_memories_chroma(query, top_k)

def _retrieve_bm25(query: str, top_k: int):
    from memory.bm25 import retrieve_memories_bm25
    return retrieve_memories_bm25(query, top_k)


def _retrieve_hybrid(query: str):
    from memory.hybrid_search import retrieve_memories_hybrid
    return retrieve_memories_hybrid(query)
