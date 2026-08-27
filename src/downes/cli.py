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
    verbose = (
        "--verbose" in sys.argv
        or "-v" in sys.argv
        or os.getenv("DOWNES_VERBOSE", "").lower() == "true"
    )
    debug = (
        "--debug" in sys.argv
        or "-d" in sys.argv
        or os.getenv("DOWNES_DEBUG", "").lower() == "true"
    )

    # Anything that is not a flag is the request. Every documented invocation
    # passes one — `downes-agent -d "Design a curriculum"` — and until now the
    # quoted text was read by nobody and silently dropped into an interactive
    # prompt, so the command appeared to hang waiting for input it had already
    # been given.
    query = " ".join(
        a
        for a in sys.argv[1:]
        if a not in ("--verbose", "-v", "--debug", "-d", "--help", "-h")
    ).strip()

    # Show help if requested
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            """
Usage: downes-agent [OPTIONS] [REQUEST]

  With a REQUEST, run it once and exit. With none, start an interactive
  session.

Options:
  -v, --verbose    Show LLM timing and token usage information
  -d, --debug      Show detailed LLM prompts, responses, and execution traces
  -h, --help       Show this help message

Environment Variables:
  DOWNES_VERBOSE   Set to 'true' to enable verbose mode
  DOWNES_DEBUG     Set to 'true' to enable debug mode

Examples:
  downes-agent "Create a Grade 9 course on photosynthesis"
  downes-agent --debug "Design a curriculum"
  downes-agent
        """
        )
        sys.exit(0)

    if debug:
        print("[DEBUG MODE ENABLED] Showing detailed LLM interactions")
    elif verbose:
        print("[VERBOSE MODE ENABLED] Showing LLM timing and token usage")

    print_intro()
    agent = Agent(verbose=verbose, debug=debug)

    # One-shot: run the request from the command line and exit. This is what
    # every example in the README and docs/ actually asks for, and it makes the
    # tool scriptable.
    if query:
        agent.run(query)
        return

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
