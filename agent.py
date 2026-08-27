"""The Gemini model loop and tool-call handling."""

import json

from google.genai import types

from clients import client
from tool_definitions import ALL_TOOLS
from tool_functions import execute_tool

RESPONSE_SCHEMA = types.Schema(
    type="OBJECT",
    properties={
        "answer": types.Schema(
        type="STRING"
        ),
        "sources_used": types.Schema(
            type="ARRAY",
            items=types.Schema(
                type="INTEGER"
                )
            )

        },
    required=["answer", "sources_used"],
)


SYSTEM_PROMPT = """You are a research assistant. Use search for current external facts.
Use memory tools only when they are relevant or the user asks you to remember something.
Never claim to have searched unless you used the search tool.
Return JSON with answer and sources_used, where sources_used contains only search result IDs."""


def run_agent(user_input: str, max_steps: int = 5) -> str:
    contents = [SYSTEM_PROMPT, user_input]
    search_results = []
    for _ in range(max_steps):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents=contents,
            config=types.GenerateContentConfig(tools=ALL_TOOLS, response_mime_type="application/json", response_schema=RESPONSE_SCHEMA),
        )
        model_content = response.candidates[0].content
        contents.append(model_content)
        function_calls = [
            part.function_call for part in model_content.parts if part.function_call
            ]
        if not function_calls:
            return _format_answer(response.text, search_results)
        for function_call in function_calls:
            result = execute_tool(
                function_call.name, dict(function_call.args or {})
                )
            if function_call.name == "search" and isinstance(result, list): #
                search_results.extend(result)

            contents.append(types.Part.from_function_response(name=function_call.name, response={"result": result}))
    return "Agent stopped: maximum steps reached."


def _format_answer(response_text: str, search_results: list[dict]) -> str:
    data = json.loads(response_text)
    answer = data["answer"]
    matched = [result for result in search_results if result["id"] in data.get("sources_used", [])]
    if matched:
        answer += "\n\n### Sources\n" + "".join(f"- [{result['title']}]({result['url']})\n" for result in matched)
    return answer
