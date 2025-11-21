from downes.agent import Agent
from downes.steps import Step
from langchain_core.messages import AIMessage
import unittest
from unittest.mock import MagicMock, patch

class TestAgentLogic(unittest.TestCase):
    def test_agent_flow(self):
        agent = Agent(verbose=True)
        
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
                return AIMessage(content="Done", tool_calls=[])
            return AIMessage(content="Done", tool_calls=[])

        agent.llm.plan_next_actions = MagicMock(side_effect=plan_next_actions_side_effect)
        
        # Mock optimize_tool_args
        agent.llm.optimize_tool_args = MagicMock(return_value={"arg": "val"})
        
        # Mock ask_if_done and is_goal_achieved to ensure they are NOT called
        agent.llm.ask_if_done = MagicMock()
        agent.llm.is_goal_achieved = MagicMock()
        
        # Mock generate_answer
        agent.llm.generate_answer = MagicMock(return_value="Final Answer")
        
        with patch('downes.agent.get_tool') as mock_get_tool, \
             patch('downes.agent.execute_tool') as mock_execute_tool, \
             patch('downes.agent.confirm_action', return_value=True):
            
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
            
            # ask_if_done should NOT be called
            agent.llm.ask_if_done.assert_not_called()
            
            # is_goal_achieved should NOT be called
            agent.llm.is_goal_achieved.assert_not_called()
            
            print("Agent flow test passed!")

if __name__ == '__main__':
    unittest.main()
