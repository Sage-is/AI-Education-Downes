"""Per-skill hard-gate patterns, ported from test_education_tools.py.

Each entry: skill -> (artifact file, required substrings). replay.py fails a
run when an expected skill's artifact is missing or a pattern is absent.
"""

CHECKS = {
    "learning-objectives": ("01_objectives.md",
        ["## Learning Objectives", "### Objectives"]),
    "syllabus": ("02_syllabus.md",
        ["Syllabus", "### Module 1"]),
    "assessments": ("03_assessments.md",
        ["## Assessments & Rubrics", "### Assessment 1"]),
    "pacing-guide": ("04_pacing.md",
        ["## Pacing Guide", "Week | Module", "### Weekly Highlights"]),
    "taxonomy-map": ("05_taxonomy.md",
        ["Taxonomy Mapping", "Objective | Level"]),
    "learning-resources": ("06_resources.md",
        ["## Synthesized Learning Resources", "Type:"]),
    "slide-deck": ("07_slides.md", ["---"]),
    "worksheet": ("08_worksheet.md",
        ["# Worksheet:", "### Differentiation"]),
}

# slide decks additionally need at least this many bare --- separator lines
MIN_SLIDE_SEPARATORS = 3
