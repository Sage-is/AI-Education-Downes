from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool


class DraftSyllabusInput(BaseModel):
    course_title: str = Field(description="Title of the course.")
    learning_objectives: List[str] = Field(
        description="List of previously generated learning objectives to align modules.")
    duration_weeks: int = Field(description="Total duration in weeks.")
    modality: str = Field(
        default="online",
        description="Delivery modality: online, in-person, hybrid.",
    )
    prerequisites: Optional[List[str]] = Field(
        default=None, description="Optional prerequisite knowledge or courses."
    )
    modules_count: int = Field(
        default=6, description="Number of modules or units to create."
    )


@tool(args_schema=DraftSyllabusInput)
def draft_syllabus(
    course_title: str,
    learning_objectives: List[str],
    duration_weeks: int,
    modality: str = "online",
    prerequisites: Optional[List[str]] = None,
    modules_count: int = 6,
) -> Dict[str, Any]:
    """
    Produces a structured syllabus outline with modules mapped to learning objectives,
    each including a description and suggested instructional strategies.
    Returns a dictionary with metadata and module breakdown.
    """
    modules: List[Dict[str, Any]] = []
    # Simple even distribution of objectives.
    obj_per_module = max(1, len(learning_objectives) // modules_count or 1)
    for i in range(modules_count):
        start = i * obj_per_module
        end = start + obj_per_module
        aligned = learning_objectives[start:end]
        if not aligned:
            aligned = learning_objectives[-obj_per_module:]
        modules.append(
            {
                "module_number": i + 1,
                "title": f"Module {i + 1}: Core Concepts",
                "summary": f"Introduces foundational elements of {course_title} with focus on applied understanding.",
                "aligned_objectives": aligned,
                "suggested_activities": [
                    "Micro-lecture",
                    "Guided discussion",
                    "Hands-on exercise",
                ],
                "formative_assessment": "Short quiz or reflective prompt",
            }
        )

    return {
        "course_title": course_title,
        "modality": modality,
        "duration_weeks": duration_weeks,
        "prerequisites": prerequisites or [],
        "modules": modules,
    }
