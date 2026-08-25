from google.genai import types

from clients import tavily_client

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

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
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
    memories = load_memories()

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
                        types="STRING",
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

ALL_TOOLS = [calculator_tool, save_note_tool, search_tool, retrieve_notes_tool, save_memory_tool, retrieve_memories_tool,]
