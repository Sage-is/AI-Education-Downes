from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.tools import tool

from downes.model import call_llm
from .utils import normalize_list_input


class MapTaxonomyInput(BaseModel):
    learning_objectives: List[str] = Field(
        description="Learning objectives to classify by the chosen taxonomy."
    )
    subject: str = Field(
        description="Subject or topic area (e.g., 'Grade 9 Science', 'Adult Drawing')."
    )
    taxonomy_type: str = Field(
        default="blooms",
        description="Taxonomy framework to apply: 'blooms', 'webb', 'solo', 'fink', or 'custom'."
    )
    custom_taxonomy_description: Optional[str] = Field(
        default=None,
        description="If taxonomy_type='custom', provide a brief description of the taxonomy framework."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "learning_objectives": [
                    "Define photosynthesis",
                    "Analyze the impact of climate change"
                ],
                "subject": "Grade 9 Science",
                "taxonomy_type": "blooms"
            }
        }
        
    @classmethod
    def normalize_learning_objectives(cls, v):
        """Normalize learning_objectives from various formats."""
        return normalize_list_input(v, default=[])


TAXONOMY_DESCRIPTIONS = {
    "blooms": """
    Bloom's Taxonomy (Revised):
    1. Remember - recall facts and basic concepts
    2. Understand - explain ideas or concepts
    3. Apply - use information in new situations
    4. Analyze - draw connections among ideas
    5. Evaluate - justify a decision or course of action
    6. Create - produce new or original work
""",
    "webb": """
    Webb's Depth of Knowledge (DOK):
    1. Recall - recall a fact, information, or procedure
    2. Skill/Concept - use information or conceptual knowledge
    3. Strategic Thinking - require reasoning, planning, using evidence
    4. Extended Thinking - require investigation, time to think and process
""",
    "solo": """
    SOLO Taxonomy (Structure of Observed Learning Outcomes):
    1. Prestructural - no real understanding
    2. Unistructural - one relevant aspect
    3. Multistructural - several relevant aspects, but not related
    4. Relational - several aspects integrated into a coherent structure
    5. Extended Abstract - generalized to new domains
""",
    "fink": """
    Fink's Taxonomy of Significant Learning:
    1. Foundational Knowledge - understanding and remembering information
    2. Application - skills, thinking, managing projects
    3. Integration - connecting ideas, people, realms of life
    4. Human Dimension - learning about oneself and others
    5. Caring - developing new feelings, interests, values
    6. Learning How to Learn - becoming a better student
"""
}


@tool(args_schema=MapTaxonomyInput)
def map_taxonomy(
    learning_objectives: List[str],
    subject: str,
    taxonomy_type: str = "blooms",
    custom_taxonomy_description: Optional[str] = None,
) -> str:
    """
        - Maps each learning objective to the appropriate level in the chosen 
          educational taxonomy framework using LLM analysis.
        - Supports Bloom's, Webb's DOK, SOLO, Fink's, or custom taxonomies.
        - Returns a Markdown formatted taxonomy mapping table.
    """
    # Normalize inputs
    learning_objectives = MapTaxonomyInput.normalize_learning_objectives(learning_objectives)
    
    if not learning_objectives:
        return "## Taxonomy Mapping\n\nNo learning objectives provided."
    
    taxonomy_type = taxonomy_type.lower()
    
    # Get taxonomy description
    if taxonomy_type == "custom":
        if not custom_taxonomy_description:
            return "## Error\n\nCustom taxonomy selected but no description provided."
        taxonomy_desc = custom_taxonomy_description
        taxonomy_name = "Custom Taxonomy"
    else:
        taxonomy_desc = TAXONOMY_DESCRIPTIONS.get(
            taxonomy_type, 
            TAXONOMY_DESCRIPTIONS["blooms"]
        )
        taxonomy_name = {
            "blooms": "Bloom's Taxonomy",
            "webb": "Webb's Depth of Knowledge",
            "solo": "SOLO Taxonomy",
            "fink": "Fink's Taxonomy"
        }.get(taxonomy_type, "Bloom's Taxonomy")
    
    # Build objectives list for prompt
    objectives_text = "\n".join([f"{i+1}. {obj}" for i, obj in enumerate(learning_objectives)])
    
    # Create LLM prompt
    system_prompt = f"""You are an expert educational taxonomist specializing in curriculum design.

Your step is to map learning objectives to the appropriate levels of the specified taxonomy framework.

{taxonomy_desc}

Analyze each learning objective carefully, considering:
- The action verbs used
- The cognitive complexity required
- The depth of understanding or skill demonstrated
- The context of the subject area

Respond ONLY with a properly formatted Markdown table. Do not include any explanation or additional text.

Format your response exactly as:

| Objective | Level | Rationale |
|-----------|-------|-----------|
| [objective text] | **[Level Name]** | [Brief justification] |

Ensure every objective is mapped to exactly one taxonomy level."""

    user_prompt = f"""Subject: {subject}

Taxonomy Framework: {taxonomy_name}

Learning Objectives to Map:
{objectives_text}

Please map each objective to the appropriate taxonomy level."""

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        
        if response and hasattr(response, 'content'):
            content = response.content.strip()
            
            # Add header if not present
            if not content.startswith("#"):
                content = f"## {taxonomy_name} Mapping\n\n{content}"
            
            return content
        else:
            # Fallback if LLM fails
            return _fallback_mapping(learning_objectives, taxonomy_name)
            
    except Exception as e:
        return f"## Error\n\nFailed to map taxonomy: {str(e)}\n\n{_fallback_mapping(learning_objectives, taxonomy_name)}"


def _fallback_mapping(objectives: List[str], taxonomy_name: str) -> str:
    """Simple fallback mapping if LLM is unavailable."""
    lines = [
        f"## {taxonomy_name} Mapping (Fallback)",
        "",
        "| Objective | Level |",
        "|-----------|-------|",
    ]
    
    for obj in objectives:
        # Simple heuristic based on common verbs
        obj_lower = obj.lower()
        if any(v in obj_lower for v in ["remember", "recall", "define", "list", "identify"]):
            level = "Remember/Recall"
        elif any(v in obj_lower for v in ["create", "design", "synthesize", "construct"]):
            level = "Create/Design"
        elif any(v in obj_lower for v in ["evaluate", "critique", "justify", "assess"]):
            level = "Evaluate"
        elif any(v in obj_lower for v in ["analyze", "compare", "differentiate", "examine"]):
            level = "Analyze"
        elif any(v in obj_lower for v in ["apply", "execute", "implement", "use"]):
            level = "Apply"
        else:
            level = "Understand"
        
        obj_display = obj[:70] + "..." if len(obj) > 70 else obj
        lines.append(f"| {obj_display} | **{level}** |")
    
    return "\n".join(lines)
