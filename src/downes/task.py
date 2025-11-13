class Task:
    """Simple task representation - no Pydantic complexity"""

    def __init__(self, id: int, description: str, done: bool = False):
        self.id = id
        self.description = description
        self.done = done

    def dict(self):
        return {"id": self.id, "description": self.description, "done": self.done}
