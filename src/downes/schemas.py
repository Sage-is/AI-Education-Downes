from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Union


class Task(BaseModel):
    """Represents a single task in a task list.

    The LLM sometimes returns symbolic IDs (e.g., "gen_obj") instead of integers.
    Accept both int and str, coercing numeric strings to int, and leaving others as str.
    """

    id: Union[int, str] = Field(..., description="Unique identifier or symbolic key for the task.")
    description: str = Field(..., description="The description of the task.")
    done: bool = Field(False, description="Whether the task is completed.")

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, v):
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            return int(v) if v.isdigit() else v
        return v


class TaskList(BaseModel):
    """Represents a list of tasks."""

    tasks: List[Task] = Field(..., description="The list of tasks.")

    @field_validator("tasks", mode="before")
    @classmethod
    def _coerce_tasks(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try to parse JSON string
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return []


class IsDone(BaseModel):
    """Represents the boolean status of a task."""

    done: bool = Field(..., description="Whether the task is done or not.")


class Answer(BaseModel):
    """Represents an answer to the user's query."""

    answer: str = Field(
        ...,
        description="A comprehensive answer to the user's query, including relevant numbers, data, reasoning, and insights.",
    )


class OptimizedToolArgs(BaseModel):
    """Represents optimized arguments for a tool call."""

    arguments: Dict[str, Any] = Field(
        ..., description="The optimized arguments dictionary for the tool call."
    )
