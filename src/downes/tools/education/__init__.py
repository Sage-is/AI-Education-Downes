from typing_extensions import Callable
from .objectives import generate_learning_objectives
from .syllabus import draft_syllabus
from .assessments import design_assessments
from .pacing import create_pacing_guide
from .taxonomy import map_taxonomy
from .resources import synthesize_learning_resources
from .slides import build_slide_deck
from .worksheet import design_worksheet

EDUCATION_TOOLS: list[Callable[..., any]] = [
    generate_learning_objectives,
    draft_syllabus,
    design_assessments,
    create_pacing_guide,
    map_taxonomy,
    synthesize_learning_resources,
    build_slide_deck,
    design_worksheet,
]
