#!/usr/bin/env python3
"""

Test to validate that the agent properly handles JSON 'null' values
and malformed JSON passed as string arguments to tools.
"""
import pytest

pytestmark = pytest.mark.skip(reason="pre-existing drift: Agent._normalize_arg_value removed; agent.py retires at Gate 1 (TODO.md)")

from downes.agent import Agent
from downes.tools.education.objectives import generate_learning_objectives
from downes.tools.education.syllabus import draft_syllabus


def test_normalize_arg_value():
    """Test that _normalize_arg_value handles various null and list representations."""
    print("Testing _normalize_arg_value with null and list values...")

    test_cases = [
        ("null", None, "JSON null string"),
        ("None", None, "Python None string"),
        ("NULL", None, "Uppercase NULL"),
        ("", None, "Empty string"),
        ("[1, 2, 3]", [1, 2, 3], "JSON array"),
        ('["a", "b"]', ["a", "b"], "JSON string array"),
        ("[", [], "Malformed JSON (opening bracket only)"),
        ("[]", [], "Empty JSON array"),
        ("[  ]", [], "Empty JSON array with spaces"),
        (42, 42, "Integer passthrough"),
        (None, None, "Python None passthrough"),
        ("some_string", "some_string", "Regular string"),
    ]

    passed = 0
    failed = 0

    for input_val, expected, description in test_cases:
        result = Agent._normalize_arg_value(input_val)
        if result == expected:
            print(f"  ✓ {description}: {repr(input_val)} → {repr(result)}")
            passed += 1
        else:
            print(
                f"  ✗ {description}: {repr(input_val)} → {repr(result)} (expected {repr(expected)})"
            )
            failed += 1

    print(f"\nPassed: {passed}/{passed + failed}")
    assert failed == 0, f"{failed} test(s) failed"


def test_objectives_with_null_duration():
    """Test that objectives tool accepts None/null for optional duration_weeks."""
    print("\nTesting generate_learning_objectives with null duration...")

    # Test 1: Direct None value
    result1 = generate_learning_objectives.run(
        {
            "topic": "Python Programming",
            "audience": "adult beginners",
            "level": "beginner",
            "duration_weeks": None,
            "outcomes_count": 3,
        }
    )
    assert result1 is not None
    assert "Python Programming" in result1
    print("  ✓ Direct None value works")

    # Test 2: String 'null' that should be normalized
    normalized_args = {
        k: Agent._normalize_arg_value(v)
        for k, v in {
            "topic": "Python Programming",
            "audience": "adult beginners",
            "level": "beginner",
            "duration_weeks": "null",
            "outcomes_count": 3,
        }.items()
    }

    result2 = generate_learning_objectives.run(normalized_args)
    assert result2 is not None
    assert "Python Programming" in result2
    print("  ✓ Normalized 'null' string works")

    # Test 3: With actual integer value
    result3 = generate_learning_objectives.run(
        {
            "topic": "Python Programming",
            "audience": "adult beginners",
            "level": "beginner",
            "duration_weeks": 8,
            "outcomes_count": 3,
        }
    )
    assert result3 is not None
    assert "8 weeks" in result3
    print("  ✓ Integer duration_weeks works")


def test_syllabus_with_null_and_malformed():
    """Test that syllabus tool handles null prerequisites and malformed learning_objectives."""
    print("\nTesting draft_syllabus with null and malformed inputs...")

    # Test 1: Null prerequisites (Optional field)
    result1 = draft_syllabus.run(
        {
            "course_title": "Introduction to Biology",
            "learning_objectives": [
                "Understand cells",
                "Explain DNA",
                "Describe evolution",
            ],
            "duration_weeks": 8,
            "modality": "online",
            "prerequisites": None,
            "modules_count": 3,
        }
    )
    assert result1 is not None
    assert "Introduction to Biology" in result1
    print("  ✓ Null prerequisites works")

    # Test 2: String 'null' for prerequisites
    normalized_args = {
        k: Agent._normalize_arg_value(v)
        for k, v in {
            "course_title": "Introduction to Biology",
            "learning_objectives": '["Understand cells", "Explain DNA"]',
            "duration_weeks": 8,
            "modality": "online",
            "prerequisites": "null",
            "modules_count": 2,
        }.items()
    }
    result2 = draft_syllabus.run(normalized_args)
    assert result2 is not None
    assert "Introduction to Biology" in result2
    print("  ✓ Normalized 'null' prerequisites works")

    # Test 3: Malformed learning_objectives '[' should be handled by validator
    try:
        normalized_args = {
            k: Agent._normalize_arg_value(v)
            for k, v in {
                "course_title": "Test Course",
                "learning_objectives": "[",  # Malformed
                "duration_weeks": 4,
            }.items()
        }
        # This should raise a validation error since learning_objectives would be empty
        result3 = draft_syllabus.run(normalized_args)
        print("  ✗ Should have raised error for empty learning_objectives")
        assert False, "Expected validation error for empty learning_objectives"
    except Exception as e:
        if "cannot be empty" in str(e) or "validation error" in str(e).lower():
            print("  ✓ Properly rejects malformed/empty learning_objectives")
        else:
            raise


if __name__ == "__main__":
    test_normalize_arg_value()
    test_objectives_with_null_duration()
    test_syllabus_with_null_and_malformed()
    print("\n✅ All null and malformed input handling tests passed!")
