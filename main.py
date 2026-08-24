from dotenv import load_dotenv
from google import genai
from google.genai import types
from tavily import TavilyClient
import os
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
    )

tavily_client=TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
    )

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


notes=[]
def save_notes(note:str):
    notes.append(note)
    return "Notes save successfully."
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


def search(query: str):
    print("Search query:", repr(query))

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    results = []

    for i, result in enumerate(response["results"], start=1):
        results.append({
            "id": i,
            "title": result["title"],
            "url": result["url"],
            "content": result["content"]
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


def execute_function(function_call):
    name=function_call.name
    args=function_call.args

    try:
        if name == "calculator":
            result = calculator(args["expression"])
        
        elif name=="save_notes":

            result = save_notes(args["note"])
                        
        
        elif name == "search":

            result = search(args["query"])

        else:
            result = f"Unknown tool: {name}"

    except Exception as e:
        result = f"Tool error: {type(e).__name__}: {e}"
        print("ERROR:", result)

    print("Tool:", name)
    print("Result:", result)

    return result


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
    search_results=[]
    system_prompt="""
            You are a research assistant.

                    For questions requiring external information:
                    1. Search for relevant information.
                    2. Use the calculator when calculations are needed.
                    3. Save useful findings when the user explicitly asks.
                    4. Never claim to have searched unless you actually used the search tool.
                    5. Use the search results to answer the question.
                    6. Return the final answer as JSON with:
                    - answer: the final answer
                    - sources_used: list of IDs of the search results used to support the answer.
                    7. Only use IDs that exist in the search results..
                    """
    contents = [system_prompt,user_input]

    for step in range(max_steps):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[calculator_tool, save_note_tool, search_tool],
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )

        model_content = response.candidates[0].content
        contents.append(model_content)

        # Gemini wants to call a tool
        has_tool_call = False
        for part in model_content.parts:
            if  part.function_call:
                has_tool_call = True
                function_call = part.function_call

                result=execute_function(function_call)

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

            answer=data["answer"]
            sources=data["sources_used"]

            if sources:
                answer += "\n\n### Sources\n"

                for source_id in sources:
                    for result in search_results:
                        if result["id"] == source_id:

                            answer += f"- [{result['title']}]({result['url']})\n"
            return answer

    return "Agent stopped: maximum steps reached."


while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    print("Agent:", run_agent(user_input))