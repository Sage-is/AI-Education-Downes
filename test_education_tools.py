from downes.tools.education.objectives import generate_learning_objectives
from downes.tools.education.syllabus import draft_syllabus
from downes.tools.education.assessments import design_assessments
from downes.tools.education.pacing import create_pacing_guide
from downes.tools.education.taxonomy import map_to_blooms_taxonomy
from downes.tools.education.resources import curate_learning_resources


def test_objectives():
    out = generate_learning_objectives.run({
        "topic": "Intro to Python",
        "audience": "adult beginners",
        "level": "beginner",
        "duration_weeks": 8,
        "outcomes_count": 4
    })
    assert isinstance(out, list) and len(out) >= 4


def test_syllabus():
    objs = [
        "Identify basic Python syntax",
        "Apply variables and control flow",
        "Implement functions",
        "Analyze simple data with lists and dicts",
    ]
    out = draft_syllabus.run({
        "course_title": "Intro to Python",
        "learning_objectives": objs,
        "duration_weeks": 8,
        "modality": "online",
        "modules_count": 4,
    })
    assert isinstance(out, dict) and "modules" in out and len(out["modules"]) == 4


def test_assessments():
    objs = [
        "Identify basic Python syntax",
        "Apply variables and control flow",
        "Implement functions",
    ]
    out = design_assessments.run({
        "learning_objectives": objs,
        "assessment_types": ["quiz", "project"],
    })
    assert isinstance(out, list) and len(out) == len(objs)


def test_pacing():
    out = create_pacing_guide.run({
        "duration_weeks": 6,
        "modules_count": 3,
        "hours_per_week": 5,
    })
    assert isinstance(out, list) and len(out) == 6


def test_taxonomy():
    objs = [
        "Describe data types",
        "Apply loops",
        "Analyze algorithm complexity",
        "Design a small program",
    ]
    out = map_to_blooms_taxonomy.run({
        "learning_objectives": objs
    })
    assert isinstance(out, list) and len(out) == len(objs)


def test_resources():
    out = curate_learning_resources.run({
        "topic": "Intro to Python",
        "max_items": 6,
    })
    assert isinstance(out, list) and len(out) == 6


if __name__ == "__main__":
    test_objectives()
    test_syllabus()
    test_assessments()
    test_pacing()
    test_taxonomy()
    test_resources()
    print("Education tools smoke tests passed.")
