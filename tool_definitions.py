"""Gemini-facing tool schemas. This module has no tool implementations."""

from google.genai import types


def _tool(name: str, description: str, properties: dict | None = None, required: list[str] | None = None):
    return types.Tool(function_declarations=[types.FunctionDeclaration(
        name=name,
        description=description,
        parameters=types.Schema(type="OBJECT", properties=properties or {}, required=required or []),
    )])


SEARCH_TOOL = _tool("search", "Search the web for current information.", {"query": types.Schema(type="STRING", description="The web search query.")}, ["query"])
SAVE_NOTE_TOOL = _tool("save_note", "Save a temporary note for this run.", {"note": types.Schema(type="STRING", description="The note to save.")}, ["note"])
RETRIEVE_NOTES_TOOL = _tool("retrieve_notes", "Retrieve temporary notes.")
SAVE_MEMORY_TOOL = _tool("save_memory", "Save information to long-term memory.", {"memory": types.Schema(type="STRING", description="Information to remember.")}, ["memory"])
RETRIEVE_MEMORY_TOOL = _tool("retrieve_memories", "Retrieve all stored long-term memories.")
VECTOR_MEMORY_TOOL = _tool("retrieve_memories_vector", "Retrieve memories using manual vector similarity.", {"query": types.Schema(type="STRING", description="Memory search query."), "top_k": types.Schema(type="INTEGER", description="Maximum results to return.")}, ["query"])
CHROMA_MEMORY_TOOL = _tool("retrieve_memories_chroma", "Retrieve memories using Chroma.", {"query": types.Schema(type="STRING", description="Memory search query."), "top_k": types.Schema(type="INTEGER", description="Maximum results to return.")}, ["query"])

ALL_TOOLS = [SEARCH_TOOL, SAVE_NOTE_TOOL, RETRIEVE_NOTES_TOOL, SAVE_MEMORY_TOOL, RETRIEVE_MEMORY_TOOL, VECTOR_MEMORY_TOOL, CHROMA_MEMORY_TOOL]
