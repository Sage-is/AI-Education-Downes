import json
import sys
from typing import Optional
from contextlib import contextmanager
from downes.utils.ui import UI
from downes.utils.logger import Logger
from downes.agent import Agent

class WebUI(UI):
    def _emit(self, type, data):
        print(json.dumps({"type": type, "data": data}), flush=True)

    def print_header(self, text):
        self._emit("header", {"text": text})

    def print_user_query(self, query):
        self._emit("user_query", {"query": query})

    def print_step_list(self, steps):
        serialized_steps = []
        for s in steps:
            if hasattr(s, 'description'):
                serialized_steps.append(s.description)
            else:
                serialized_steps.append(str(s))
        self._emit("step_list", {"steps": serialized_steps})

    def print_step_start(self, step_desc):
        self._emit("step_start", {"description": step_desc})

    def print_step_done(self, step_desc):
        self._emit("step_done", {"description": step_desc})

    def print_tool_params(self, params):
        self._emit("tool_params", {"params": params})

    def print_tool_run(self, result):
        self._emit("tool_run", {"result": result})

    def print_answer(self, answer):
        self._emit("answer", {"answer": answer})

    def print_info(self, message):
        self._emit("info", {"message": message})

    def print_error(self, message):
        self._emit("error", {"message": message})

    def print_warning(self, message):
        self._emit("warning", {"message": message})

    @contextmanager
    def progress(self, message: str, success_message: str = ""):
        self._emit("progress_start", {"message": message})
        try:
            yield
            self._emit("progress_end", {"message": success_message})
        except Exception as e:
            self._emit("progress_fail", {"message": str(e)})
            raise

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"type": "error", "data": {"message": "No query provided"}}))
        sys.exit(1)

    query = sys.argv[1]
    
    web_ui = WebUI()
    logger = Logger(verbose=False, ui=web_ui)
    agent = Agent(verbose=False, debug=False, logger=logger)
    
    try:
        agent.run(query)
    except Exception as e:
        web_ui.print_error(str(e))

if __name__ == "__main__":
    main()
