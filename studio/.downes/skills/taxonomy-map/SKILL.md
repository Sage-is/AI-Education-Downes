---
name: taxonomy-map
description: Map learning objectives to the levels of a taxonomy framework — Bloom's, Webb's DOK, SOLO, or Fink's. Use when the user asks for taxonomy mapping, cognitive levels, or Bloom's alignment, or when a course plan names 05_taxonomy.md.
---

# Mapping objectives to a taxonomy

## Inputs to gather (ask if missing)

- learning_objectives (read `01_objectives.md` if present; required)
- taxonomy (default: blooms; one of blooms / webb / solo / fink / custom —
  for custom, ask the user for a description first)

## Reference: the four frameworks

### Bloom's Taxonomy (Revised)

1. Remember - recall facts and basic concepts
2. Understand - explain ideas or concepts
3. Apply - use information in new situations
4. Analyze - draw connections among ideas
5. Evaluate - justify a decision or course of action
6. Create - produce new or original work

### Webb's Depth of Knowledge (DOK)

1. Recall - recall a fact, information, or procedure
2. Skill/Concept - use information or conceptual knowledge
3. Strategic Thinking - require reasoning, planning, using evidence
4. Extended Thinking - require investigation, time to think and process

### SOLO Taxonomy (Structure of Observed Learning Outcomes)

1. Prestructural - no real understanding
2. Unistructural - one relevant aspect
3. Multistructural - several relevant aspects, but not related
4. Relational - several aspects integrated into a coherent structure
5. Extended Abstract - generalized to new domains

### Fink's Taxonomy of Significant Learning

1. Foundational Knowledge - understanding and remembering information
2. Application - skills, thinking, managing projects
3. Integration - connecting ideas, people, realms of life
4. Human Dimension - learning about oneself and others
5. Caring - developing new feelings, interests, values
6. Learning How to Learn - becoming a better student

## Method

You are an expert educational taxonomist specializing in curriculum design.
Map each learning objective to the appropriate level of the chosen
framework. Analyze each objective carefully, considering:

- The action verbs used
- The cognitive complexity required
- The depth of understanding or skill demonstrated
- The context of the subject area

## Output contract

Write `05_taxonomy.md` in the current course folder. The file must contain
only: a `## Taxonomy Mapping` heading, one line naming the framework used,
then a strict Markdown table `| Objective | Level | Rationale |` with every
objective mapped exactly once. No explanation outside the table.
