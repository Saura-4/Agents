"""Application entry point."""

from agent import run_agent
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            return
        print("Agent:", run_agent(user_input))


if __name__ == "__main__":
    main()
