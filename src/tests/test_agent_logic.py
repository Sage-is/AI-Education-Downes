from downes.agent import (
    Agent,
    cleanup_llm_artifact_content,
    indicates_tool_permission_issue,
    infer_fallback_tool_call,
)
from downes.steps import Step
from langchain_core.messages import AIMessage
import unittest
from unittest.mock import MagicMock, patch

class TestAgentLogic(unittest.TestCase):
    def test_agent_flow(self):
        agent = Agent(verbose=True)
        agent.logger.ui.prompt_for_input = MagicMock(return_value='n')
        
        # Mock LLM methods
        agent.llm.plan_steps = MagicMock(return_value=[
            Step(id=1, description="Step 1", done=False),
            Step(id=2, description="Step 2", done=False)
        ])
        
        # plan_next_actions returns a tool call first, then empty (done)
        # For Step 1: Tool call -> Done
        # For Step 2: Done immediately
        
        # Side effect for plan_next_actions
        def plan_next_actions_side_effect(step_desc, last_outputs=""):
            if step_desc == "Step 1":
                if "Tool output" in last_outputs:
                    return AIMessage(content="Done", tool_calls=[])
                else:
                    return AIMessage(content="Call tool", tool_calls=[{"name": "mock_tool", "args": {"arg": "val"}, "id": "call_1"}])
            elif step_desc == "Step 2":
                return AIMessage(content="Here is a direct step result generated without tool calls.", tool_calls=[])
            return AIMessage(content="Done", tool_calls=[])

        agent.llm.plan_next_actions = MagicMock(side_effect=plan_next_actions_side_effect)

        # Mock generate_answer
        agent.llm.generate_answer = MagicMock(return_value="Final Answer")

        with patch('downes.agent.get_tool') as mock_get_tool, \
             patch('downes.agent.execute_tool') as mock_execute_tool, \
               patch('downes.agent.confirm_action', return_value=True), \
               patch.object(agent.vault, 'save_artifact') as mock_save_artifact:
            
            mock_tool = MagicMock()
            mock_get_tool.return_value = mock_tool
            mock_execute_tool.return_value = "Tool output"
            
            agent.run("Test Query")
            
            # Assertions
            agent.llm.plan_steps.assert_called_once()
            
            # plan_next_actions should be called:
            # 1. Step 1 (initial) -> returns tool call
            # 2. Step 1 (after tool) -> returns empty
            # 3. Step 2 (initial) -> returns empty
            self.assertEqual(agent.llm.plan_next_actions.call_count, 3)

            llm_response_calls = [
                call for call in mock_save_artifact.call_args_list
                if call.kwargs.get('artifact_name', '').endswith('llm_response')
            ]
            self.assertGreaterEqual(len(llm_response_calls), 1)
            
            print("Agent flow test passed!")

    def test_cleanup_llm_artifact_prefers_fenced_payload(self):
        raw = """
        I'll create the deck now.

        ---

        ```markdown
        # Slide 1
        Content
        ```

        ---

        How to use this deck...
        """
        cleaned = cleanup_llm_artifact_content(raw)
        self.assertIn("# Slide 1", cleaned)
        self.assertIn("Content", cleaned)
        self.assertNotIn("How to use this deck", cleaned)

    def test_permission_issue_detection_and_fallback(self):
        self.assertTrue(
            indicates_tool_permission_issue(
                "I don't have permission for web search or web fetch tools in this session"
            )
        )
        fallback = infer_fallback_tool_call(
            "Synthesize 8 learning resources from .edu and OER sources"
        )
        self.assertIsNotNone(fallback)
        self.assertEqual(fallback["name"], "searx_search")

if __name__ == '__main__':
    unittest.main()
