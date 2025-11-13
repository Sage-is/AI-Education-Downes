from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

from downes.agent import Agent
from downes.utils.intro import print_intro
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


def main():
    # Parse command line arguments for verbose/debug flags
    verbose = "--verbose" in sys.argv or "-v" in sys.argv or os.getenv("DOWNES_VERBOSE", "").lower() == "true"
    debug = "--debug" in sys.argv or "-d" in sys.argv or os.getenv("DOWNES_DEBUG", "").lower() == "true"
    
    # Show help if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Usage: downes [OPTIONS]

Options:
  -v, --verbose    Show LLM timing and token usage information
  -d, --debug      Show detailed LLM prompts, responses, and execution traces
  -h, --help       Show this help message

Environment Variables:
  DOWNES_VERBOSE   Set to 'true' to enable verbose mode
  DOWNES_DEBUG     Set to 'true' to enable debug mode
        """)
        sys.exit(0)
    
    if debug:
        print("[DEBUG MODE ENABLED] Showing detailed LLM interactions")
    elif verbose:
        print("[VERBOSE MODE ENABLED] Showing LLM timing and token usage")
    
    print_intro()
    agent = Agent(verbose=verbose, debug=debug)

    # Create a prompt session
    session = PromptSession(history=InMemoryHistory())

    while True:
        try:
            # Prompt the user for input
            query = session.prompt(">> ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if query:
                # Run the agent
                agent.run(query)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
