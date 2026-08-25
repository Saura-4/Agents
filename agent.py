import json

from google.genai import types

from clients import client
from executor import execute_function
from tools import ALL_TOOLS

response_schema = types.Schema(
    type="OBJECT",
    properties={
        "answer": types.Schema(
            type="STRING"
        ),
        "sources_used": types.Schema(
            type="ARRAY",
            items=types.Schema(type="INTEGER")
        )
    },
    required=["answer", "sources_used"]
)


def run_agent(user_input, max_steps=5):
    search_results = []

    system_prompt = """
        You are a research assistant.

        For questions requiring external information:
        1. Search for relevant information.
        2. Use the calculator when calculations are needed.
        3. Save information to long-term memory when the user explicitly asks you to remember something.
        4. Retrieve long-term memories when they may be relevant to the current request.
        5. Never claim to have searched unless you actually used the search tool.
        6. Use the search results to answer the question.
        7. Return the final answer as JSON with:
        - answer: the final answer
        - sources_used: list of IDs of the search results used to support the answer.
        8. Only use IDs that exist in the search results.
        """

    contents = [system_prompt, user_input]

    for step in range(max_steps):

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=ALL_TOOLS,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        )

        model_content = response.candidates[0].content
        contents.append(model_content)

        # Gemini wants to call a tool
        has_tool_call = False
        for part in model_content.parts:
            if part.function_call:
                has_tool_call = True
                function_call = part.function_call

                result = execute_function(function_call)

                if function_call.name == "search":
                    search_results.extend(result)

                tool_response = types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": result},
                )
                contents.append(tool_response)

        # Gemini has produced the final answer
        if not has_tool_call:
            data = json.loads(response.text)

            answer = data["answer"]
            sources = data["sources_used"]

            if sources:
                answer += "\n\n### Sources\n"

                for source_id in sources:
                    for result in search_results:
                        if result["id"] == source_id:
                            answer += f"- [{result['title']}]({result['url']})\n"

            return answer

    return "Agent stopped: maximum steps reached."
