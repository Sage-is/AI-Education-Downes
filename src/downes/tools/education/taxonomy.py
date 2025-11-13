from typing import List
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool


class MapToBloomsInput(BaseModel):
    learning_objectives: List[str] = Field(
        description="Learning objectives to classify by Bloom's taxonomy."
    )

    @field_validator("learning_objectives", mode="before")
    @classmethod
    def _coerce_objectives(cls, v):
        if v is None or isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON/Python-list string first, then comma-separated
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                try:
                    import ast

                    parsed = ast.literal_eval(v)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


@tool(args_schema=MapToBloomsInput)
def map_to_blooms_taxonomy(learning_objectives: List[str]) -> str:
    """
    Maps each learning objective to a Bloom's taxonomy level
    based on indicative action verbs.
    Returns Markdown formatted taxonomy mapping.
    """
    verb_map = {
        "remember": ["define", "list", "recall", "identify"],
        "understand": ["describe", "explain", "summarize"],
        "apply": ["apply", "execute", "implement"],
        "analyze": ["analyze", "compare", "differentiate"],
        "evaluate": ["evaluate", "critique", "justify"],
        "create": ["create", "design", "construct", "synthesize"],
    }

    def classify(obj: str) -> str:
        low = obj.lower()
        for level, verbs in verb_map.items():
            for v in verbs:
                if v in low:
                    return level
        return "understand"

    lines = [
        "## Bloom's Taxonomy Mapping",
        "",
        "Cognitive levels for each learning objective:",
        "",
        "| Objective | Bloom's Level |",
        "|-----------|---------------|",
    ]

    for obj in learning_objectives:
        level = classify(obj)
        lines.append(
            f"| {obj[:60]}{'...' if len(obj) > 60 else ''} | **{level.capitalize()}** |"
        )

    return "\n".join(lines)
