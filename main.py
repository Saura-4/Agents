from agent import run_agent


while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    print("Agent:", run_agent(user_input))
