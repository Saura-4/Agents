from tools import calculator, save_notes, retrieve_notes, search, save_memory, retrieve_memories, retrieve_last_n_memories, retrieve_memories_vector


def execute_function(function_call):
    name = function_call.name
    args = function_call.args

    try:
        if name == "calculator":
            result = calculator(args["expression"])

        elif name == "save_notes":
            result = save_notes(args["note"])

        elif name == "retrieve_notes":
            result = retrieve_notes()

        elif name == "search":
            result = search(args["query"])

        elif name == "save_memory":
            result = save_memory(args["memory"])

        elif name == "retrieve_memories":
            result = retrieve_memories()

        elif name == "retrieve_last_n_memories":
            result = retrieve_last_n_memories(args["n"])

        elif name == "retrieve_memories_vector":
            result = retrieve_memories_vector(args["query"])
            
        else:
            result = f"Unknown tool: {name}"


    except Exception as e:
        result = f"Tool error: {type(e).__name__}: {e}"
        print("ERROR:", result)

    print("Tool:", name)
    print("Result:", result)

    return result
