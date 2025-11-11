from typing_extensions import Callable
from .objectives import generate_learning_objectives
from .syllabus import draft_syllabus
from .assessments import design_assessments
from .pacing import create_pacing_guide
from .taxonomy import map_to_blooms_taxonomy
from .resources import curate_learning_resources

EDUCATION_TOOLS: list[Callable[..., any]] = [
    generate_learning_objectives,
    draft_syllabus,
    design_assessments,
    create_pacing_guide,
    map_to_blooms_taxonomy,
    curate_learning_resources,
]
