from downes.tools.education.objectives import generate_learning_objectives
from downes.tools.education.syllabus import draft_syllabus
from downes.tools.education.assessments import design_assessments
from downes.tools.education.pacing import create_pacing_guide
from downes.tools.education.taxonomy import map_taxonomy
from downes.tools.education.resources import synthesize_learning_resources
from downes.tools.education.slides import build_slide_deck
from downes.tools.education.worksheet import design_worksheet


def test_objectives():
    """Test objectives tool returns Markdown"""
    out = generate_learning_objectives.run(
        {
            "topic": "Intro to Python",
            "audience": "adult beginners",
            "level": "beginner",
            "duration_weeks": 8,
            "outcomes_count": 4,
        }
    )
    assert isinstance(out, str)
    assert "## Learning Objectives" in out
    assert "Intro to Python" in out
    assert "adult beginners" in out
    print("✓ Objectives test passed")


def test_syllabus():
    """Test syllabus tool returns Markdown"""
    objs = [
        "Identify basic Python syntax",
        "Apply variables and control flow",
        "Implement functions",
        "Analyze simple data with lists and dicts",
    ]
    out = draft_syllabus.run(
        {
            "course_title": "Intro to Python",
            "learning_objectives": objs,
            "duration_weeks": 8,
            "modality": "online",
            "modules_count": 4,
        }
    )
    assert isinstance(out, str)
    assert "# Intro to Python - Syllabus" in out
    assert "## Course Modules" in out
    assert "### Module 1:" in out
    print("✓ Syllabus test passed")


def test_assessments():
    """Test assessments tool returns Markdown"""
    objs = [
        "Identify basic Python syntax",
        "Apply variables and control flow",
        "Implement functions",
    ]
    out = design_assessments.run(
        {
            "learning_objectives": objs,
            "assessment_types": ["quiz", "project"],
        }
    )
    assert isinstance(out, str)
    assert "## Assessments & Rubrics" in out
    assert "### Assessment 1:" in out
    assert "Criterion" in out and "Weight" in out
    print("✓ Assessments test passed")


def test_pacing():
    """Test pacing guide returns Markdown"""
    out = create_pacing_guide.run(
        {
            "duration_weeks": 6,
            "modules_count": 3,
            "hours_per_week": 5,
        }
    )
    assert isinstance(out, str)
    assert "## Pacing Guide" in out
    assert "Week | Module" in out
    assert "6 weeks" in out
    print("✓ Pacing test passed")


def test_taxonomy():
    """Test taxonomy mapping returns Markdown"""
    objs = [
        "Describe data types",
        "Apply loops",
        "Analyze algorithm complexity",
        "Design a small program",
    ]

    # Test with Bloom's taxonomy
    out = map_taxonomy.run(
        {
            "learning_objectives": objs,
            "subject": "Intro to Python",
            "taxonomy_type": "blooms",
        }
    )
    assert isinstance(out, str)
    assert "Mapping" in out
    assert "Objective" in out and "Level" in out
    print("✓ Taxonomy test (Bloom's) passed")

    # Test with Webb's DOK
    out_webb = map_taxonomy.run(
        {
            "learning_objectives": objs[:2],
            "subject": "Python Programming",
            "taxonomy_type": "webb",
        }
    )
    assert isinstance(out_webb, str)
    assert "Mapping" in out_webb
    assert "Objective" in out_webb
    print("✓ Taxonomy test (Webb's) passed")


def test_resources():
    """Test resources tool returns Markdown"""
    out = synthesize_learning_resources.run(
        {
            "topic": "Intro to Python",
            "max_items": 6,
        }
    )
    assert isinstance(out, str)
    assert "## Synthesized Learning Resources" in out
    assert "Intro to Python" in out
    assert "Type:" in out
    print("✓ Resources test passed")


def test_slides():
    """Test slide deck tool returns reveal.js formatted Markdown"""
    out = build_slide_deck.run(
        {
            "topic": "Intro to Python",
            "audience": "high school programming club",
            "slide_count": 6,
            "learning_objectives": [
                "Explain why Python is popular",
                "Demonstrate variables",
            ],
            "call_to_action": "Share a simple script in the chat",
        }
    )
    assert isinstance(out, str)
    assert "#" in out and "---" in out
    assert "Intro to Python" in out
    print("✓ Slides test passed")


def test_worksheet():
    """Test worksheet tool returns structured Markdown"""
    out = design_worksheet.run(
        {
            "topic": "Intro to Python",
            "audience": "Grade 9 CS",
            "skill_focus": "Writing simple programs",
            "learning_objectives": [
                "Trace simple input/output",
                "Write a script that prints a message",
            ],
            "materials": ["Laptop"],
        }
    )
    assert isinstance(out, str)
    assert "Worksheet" in out
    assert "Differentiation" in out
    print("✓ Worksheet test passed")


if __name__ == "__main__":
    test_objectives()
    test_syllabus()
    test_assessments()
    test_pacing()
    test_taxonomy()
    test_resources()
    test_slides()
    test_worksheet()
    print("\n✅ All education tools smoke tests passed!")
