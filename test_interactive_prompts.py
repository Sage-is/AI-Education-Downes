#!/usr/bin/env python3
"""
Test script for interactive prompt editing in debug mode.

This demonstrates the new interactive features:
- Prompt preview before submission
- Option to edit user prompt
- Option to edit system prompt
- Option to view full prompts
- Option to cancel LLM calls

Usage:
    python test_interactive_prompts.py

Or with the agent:
    uv run downes-agent --debug "Create a Python basics course"
"""

from downes.utils.logger import Logger
from downes.llm_interaction import _review_and_edit_prompt

def test_interactive_prompt():
    """Test the interactive prompt review feature."""
    
    logger = Logger(verbose=True)
    
    print("\n" + "="*80)
    print("INTERACTIVE PROMPT EDITING TEST")
    print("="*80 + "\n")
    
    # Sample prompts
    system_prompt = """You are an expert curriculum developer specializing in creating 
engaging, age-appropriate educational content. Your role is to:
- Design clear learning objectives aligned with educational standards
- Create structured lesson plans with appropriate pacing
- Develop assessment strategies that measure student understanding
- Recommend relevant educational resources and materials"""

    user_prompt = """Create a 6-week course on Python programming for high school students.
    
The course should:
- Be suitable for complete beginners
- Include hands-on coding exercises
- Cover fundamental programming concepts
- Build toward a final project"""

    operation_name = "Course Planning Test"
    
    # Call the interactive review
    edited_user_prompt, edited_system_prompt = _review_and_edit_prompt(
        user_prompt,
        system_prompt,
        operation_name,
        logger
    )
    
    if edited_user_prompt is None:
        print("\n❌ LLM call was cancelled by user\n")
    else:
        print("\n✅ Prompts approved for submission!\n")
        print("Final User Prompt Length:", len(edited_user_prompt), "chars")
        print("Final System Prompt Length:", len(edited_system_prompt), "chars")
        
        if edited_user_prompt != user_prompt:
            print("\n📝 User prompt was modified")
        if edited_system_prompt != system_prompt:
            print("\n📝 System prompt was modified")

if __name__ == "__main__":
    print("""
This test demonstrates the interactive prompt editing feature.
In debug mode, you can:
    
    [s] Submit as-is     - Send the prompt to the LLM unchanged
    [e] Edit user prompt - Modify the user prompt in your editor
    [E] Edit system prompt - Modify the system prompt in your editor
    [v] View full prompts - See complete prompts without truncation
    [c] Cancel - Skip this LLM call entirely
    
Your EDITOR environment variable determines which editor opens.
Default: nano (set EDITOR=vim, EDITOR=code, etc. to change)
    """)
    
    try:
        test_interactive_prompt()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
