from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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

def run_agent(user_input):
    contents = [user_input]

    while True:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[calculator_tool]
            )
        )

        model_content = response.candidates[0].content
        contents.append(model_content)

        # Gemini wants to call a tool
        if model_content.parts[0].function_call:
            function_call = model_content.parts[0].function_call

            if function_call.name == "calculator":
                expression = function_call.args["expression"]

                result = calculator(expression)

                print("Tool:", expression)
                print("Result:", result)

                tool_response = types.Part.from_function_response(
                    name="calculator",
                    response={"result": result},
                )

                contents.append(tool_response)

        # Gemini has produced the final answer
        else:
            return response.text


while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    print("Agent:", run_agent(user_input))