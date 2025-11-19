"""
Education tools sanity tests.

Verifies core curriculum-development tools respond and return
expected structures without relying on external APIs.
"""

from downes.tools.education.objectives import generate_learning_objectives
from downes.tools.education.syllabus import draft_syllabus
from downes.tools.education.assessments import design_assessments
from downes.tools.education.pacing import create_pacing_guide
from downes.tools.education.taxonomy import map_to_blooms_taxonomy
from downes.tools.education.resources import synthesize_learning_resources


def test_objectives():
    print("Testing: generate_learning_objectives …")
    out = generate_learning_objectives.run(
        {
            "topic": "Data Visualization",
            "audience": "undergraduate beginners",
            "level": "beginner",
            "duration_weeks": 6,
            "outcomes_count": 4,
        }
    )
    assert isinstance(out, list) and len(out) >= 4
    print(f"✓ Objectives generated: {len(out)}")


def test_syllabus():
    print("Testing: draft_syllabus …")
    objs = [
        "Identify basic chart types",
        "Apply design principles to visual encodings",
        "Analyze datasets to select appropriate visuals",
        "Create static and interactive charts",
    ]
    syl = draft_syllabus.run(
        {
            "course_title": "Foundations of Data Visualization",
            "learning_objectives": objs,
            "duration_weeks": 6,
            "modality": "online",
            "modules_count": 3,
        }
    )
    assert isinstance(syl, dict) and "modules" in syl and len(syl["modules"]) == 3
    print(f"✓ Syllabus modules: {len(syl['modules'])}")


def test_assessments():
    print("Testing: design_assessments …")
    objs = [
        "Identify basic chart types",
        "Apply design principles to visual encodings",
        "Create static and interactive charts",
    ]
    assessments = design_assessments.run(
        {
            "learning_objectives": objs,
            "assessment_types": ["quiz", "project", "presentation"],
        }
    )
    assert isinstance(assessments, list) and len(assessments) == len(objs)
    print(f"✓ Assessments aligned: {len(assessments)}")


def test_pacing():
    print("Testing: create_pacing_guide …")
    weeks = create_pacing_guide.run(
        {
            "duration_weeks": 6,
            "modules_count": 3,
            "hours_per_week": 5,
        }
    )
    assert isinstance(weeks, list) and len(weeks) == 6
    print(f"✓ Weeks planned: {len(weeks)}")


def test_taxonomy():
    print("Testing: map_to_blooms_taxonomy …")
    objs = [
        "Describe data types",
        "Apply color theory",
        "Analyze dashboard usability",
        "Design an infographic",
    ]
    mapping = map_to_blooms_taxonomy.run({"learning_objectives": objs})
    assert isinstance(mapping, list) and len(mapping) == len(objs)
    print(f"✓ Objectives mapped: {len(mapping)}")


def test_resources():
    print("Testing: synthesize_learning_resources …")
    res = synthesize_learning_resources.run(
        {
            "topic": "Data Visualization",
            "max_items": 5,
        }
    )
    assert isinstance(res, list) and len(res) == 5
    print(f"✓ Resources synthesized: {len(res)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Downes Education Tools")
    print("=" * 60)
    print()

    test_objectives()
    test_syllabus()
    test_assessments()
    test_pacing()
    test_taxonomy()
    test_resources()

    print()
    print("=" * 60)
    print("Tests Complete!")
    print("=" * 60)
    print("\n✓ Education tools are working correctly!")
    print("  - Deterministic scaffolds, no external APIs required")
    print("  - Ready to use via: uv run downes-agent")
