# Taxonomy Tool Refactor

## Overview

The taxonomy mapping tool has been refactored from a simple rule-based approach to an LLM-powered solution that provides more reliable and context-aware taxonomy mappings.

## Changes

### Tool Name
- **Old:** `map_to_blooms_taxonomy`
- **New:** `map_taxonomy`

### Key Improvements

1. **Multiple Taxonomy Support**
   - Bloom's Taxonomy (Revised)
   - Webb's Depth of Knowledge (DOK)
   - SOLO Taxonomy
   - Fink's Taxonomy of Significant Learning
   - Custom taxonomies (user-defined)

2. **LLM-Powered Analysis**
   - Instead of simple keyword matching, the tool now uses LLM reasoning to analyze each learning objective
   - Considers context, action verbs, cognitive complexity, and subject area
   - Provides rationale for each mapping decision

3. **Context-Aware**
   - Takes subject/topic into account when mapping objectives
   - Adapts to different educational levels and contexts

4. **Robust Output**
   - Returns well-formatted Markdown tables
   - Includes rationale column explaining the taxonomy level choice
   - Fallback mechanism if LLM is unavailable

## Usage Examples

### Bloom's Taxonomy (Default)
```python
from downes.tools.education.taxonomy import map_taxonomy

objectives = [
    "Define photosynthesis",
    "Apply scientific methods to investigate phenomena",
    "Evaluate the impact of climate change"
]

result = map_taxonomy.run({
    "learning_objectives": objectives,
    "subject": "Grade 9 Science",
    "taxonomy_type": "blooms"
})
```

### Webb's Depth of Knowledge
```python
result = map_taxonomy.run({
    "learning_objectives": objectives,
    "subject": "High School Biology",
    "taxonomy_type": "webb"
})
```

### SOLO Taxonomy
```python
result = map_taxonomy.run({
    "learning_objectives": objectives,
    "subject": "Introduction to Psychology",
    "taxonomy_type": "solo"
})
```

### Fink's Taxonomy
```python
result = map_taxonomy.run({
    "learning_objectives": objectives,
    "subject": "Adult Learning Theory",
    "taxonomy_type": "fink"
})
```

### Custom Taxonomy
```python
result = map_taxonomy.run({
    "learning_objectives": objectives,
    "subject": "Art History",
    "taxonomy_type": "custom",
    "custom_taxonomy_description": """
    Artistic Understanding Taxonomy:
    1. Recognition - identify artists and styles
    2. Interpretation - explain artistic choices
    3. Analysis - compare works and movements
    4. Synthesis - connect art to historical context
    5. Creation - produce original artistic work
    """
})
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `learning_objectives` | List[str] | Yes | - | Learning objectives to classify |
| `subject` | str | Yes | - | Subject or topic area |
| `taxonomy_type` | str | No | "blooms" | Taxonomy framework: 'blooms', 'webb', 'solo', 'fink', or 'custom' |
| `custom_taxonomy_description` | str | No | None | Description of custom taxonomy (required if taxonomy_type='custom') |

## Output Format

The tool returns a Markdown table with:
- **Objective:** The learning objective text
- **Level:** The taxonomy level (bolded)
- **Rationale:** Brief explanation of why this level was chosen

Example output:

```markdown
## Bloom's Taxonomy Mapping

| Objective | Level | Rationale |
|-----------|-------|-----------|
| Define photosynthesis and cellular respiration | **Understand** | The objective requires explaining complex concepts, indicating comprehension rather than recall. |
| Apply scientific methods to investigate natural phenomena | **Apply** | The verb "apply" suggests using information in new situations, implying hands-on experimentation. |
| Evaluate the impact of human activity on biodiversity | **Evaluate** | Justifying decisions requires critical thinking about complex environmental issues. |
```

## Migration Guide

### For Agent Users
The tool is backward compatible when used by the agent - it will automatically adapt to the new interface.

### For Direct API Users

**Old code:**
```python
from downes.tools.education.taxonomy import map_to_blooms_taxonomy

result = map_to_blooms_taxonomy.run({
    "learning_objectives": ["Define X", "Apply Y"]
})
```

**New code:**
```python
from downes.tools.education.taxonomy import map_taxonomy

result = map_taxonomy.run({
    "learning_objectives": ["Define X", "Apply Y"],
    "subject": "Your Subject Here",
    "taxonomy_type": "blooms"  # optional, defaults to blooms
})
```

## Benefits

1. **More Accurate:** LLM reasoning provides better taxonomy classification than simple keyword matching
2. **More Flexible:** Supports multiple taxonomy frameworks and custom taxonomies
3. **More Transparent:** Includes rationale for each classification
4. **Context-Aware:** Considers the subject matter when making classifications
5. **More Reliable:** Provides consistent, well-reasoned mappings across different educational contexts

## Technical Details

- Uses the same LLM infrastructure as other Downes tools
- Includes fallback mechanism for when LLM is unavailable
- Properly validates and normalizes input (supports lists, JSON strings, comma-separated strings)
- Follows the same patterns as other education tools (objectives, syllabus, etc.)
