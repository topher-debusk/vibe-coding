"""Tests for orchestrator.py"""
import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from vibe_coding.orchestrator import orchestrator
from vibe_coding.utils import save_state, load_state, TOOLS


class TestOrchestrator(unittest.TestCase):
    """Tests for the orchestrator function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary file for state
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "agent_state.json")
        
        # Patch the STATE_FILE location
        self.state_file_patcher = patch('vibe_coding.utils.STATE_FILE', self.state_file)
        self.state_file_patcher.start()
        
        # Create a temporary input file
        self.input_file = os.path.join(self.temp_dir, "test_input.txt")
        with open(self.input_file, "w") as f:
            f.write("First task. Second task. Third task.")
        
        # Create mock args
        self.args = SimpleNamespace(input=self.input_file)

    def tearDown(self):
        """Clean up after tests"""
        self.state_file_patcher.stop()
        
        # Clean up temporary files
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        os.rmdir(self.temp_dir)

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_runs_tools_in_sequence(self, mock_ai):
        """Test that orchestrator runs tools in the correct sequence"""
        mock_ai.return_value = "Summary text."
        
        with patch('builtins.print'):  # Suppress print output
            orchestrator(self.args)
        
        # ai_call should be called once for summarize
        mock_ai.assert_called()

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_updates_state(self, mock_ai):
        """Test that orchestrator updates state correctly"""
        mock_ai.return_value = "Summary text."
        
        with patch('builtins.print'):  # Suppress print output
            orchestrator(self.args)
        
        # Load state and verify it was updated
        state = load_state()
        self.assertIn("summarize", state)
        self.assertIn("todo", state)
        self.assertEqual(state["summarize"], "Summary text.")

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_todo_output_format(self, mock_ai):
        """Test that orchestrator generates todos in correct format"""
        mock_ai.return_value = "Summary text."
        
        with patch('builtins.print'):  # Suppress print output
            orchestrator(self.args)
        
        state = load_state()
        todos = state.get("todo", [])
        
        # Verify todos are formatted as list items
        self.assertGreater(len(todos), 0)
        self.assertTrue(all(item.startswith("- ") for item in todos))

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_chains_output(self, mock_ai):
        """Test that orchestrator chains output (summarize -> todo)"""
        mock_ai.return_value = "Summary text. More summary."
        
        with patch('builtins.print'):  # Suppress print output
            orchestrator(self.args)
        
        state = load_state()
        todos = state.get("todo", [])
        
        # The todos should be generated from the summary output
        # Since summary is "Summary text. More summary.", we should get 2 todos
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], "- Summary text")
        self.assertEqual(todos[1], "- More summary")

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_file_not_found(self, mock_ai):
        """Test orchestrator handles missing input file"""
        bad_args = SimpleNamespace(input="/nonexistent/file.txt")
        
        with patch('builtins.print') as mock_print:
            orchestrator(bad_args)
        
        # Should print error message
        mock_print.assert_called()
        error_call = [call for call in mock_print.call_args_list 
                      if "not found" in str(call)]
        self.assertTrue(len(error_call) > 0)

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_preserves_existing_state(self, mock_ai):
        """Test that orchestrator preserves existing state"""
        mock_ai.return_value = "New summary."
        
        # Save initial state
        initial_state = {"previous_key": "previous_value"}
        save_state(initial_state)
        
        with patch('builtins.print'):  # Suppress print output
            orchestrator(self.args)
        
        # Load final state and verify it preserves old key
        final_state = load_state()
        self.assertEqual(final_state["previous_key"], "previous_value")
        self.assertIn("summarize", final_state)

    @patch('vibe_coding.utils.ai_call')
    def test_orchestrator_output_messages(self, mock_ai):
        """Test that orchestrator prints appropriate messages"""
        mock_ai.return_value = "Summary."
        
        with patch('builtins.print') as mock_print:
            orchestrator(self.args)
        
        # Check for key output messages
        print_calls = [str(call) for call in mock_print.call_args_list]
        print_str = " ".join(print_calls)
        
        self.assertIn("Orchestrator Starting", print_str)
        self.assertIn("Orchestrator Finished", print_str)

    def test_orchestrator_with_multiple_tools(self):
        """Test that orchestrator accesses multiple tools from TOOLS registry"""
        # Verify both tools are registered
        self.assertIn("summarize", TOOLS)
        self.assertIn("todo", TOOLS)
        
        # Verify tools have callable functions
        self.assertTrue(callable(TOOLS["summarize"]["fn"]))
        self.assertTrue(callable(TOOLS["todo"]["fn"]))


class TestOrchestratorStateManagement(unittest.TestCase):
    """Tests for orchestrator state management"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "agent_state.json")
        
        # Patch the STATE_FILE location
        self.state_file_patcher = patch('vibe_coding.utils.STATE_FILE', self.state_file)
        self.state_file_patcher.start()
        
        self.input_file = os.path.join(self.temp_dir, "test_input.txt")
        with open(self.input_file, "w") as f:
            f.write("Task 1. Task 2.")
        
        self.args = SimpleNamespace(input=self.input_file)

    def tearDown(self):
        """Clean up after tests"""
        self.state_file_patcher.stop()
        
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        os.rmdir(self.temp_dir)

    @patch('vibe_coding.utils.ai_call')
    def test_state_file_is_created(self, mock_ai):
        """Test that state file is created after orchestrator runs"""
        mock_ai.return_value = "Summary."
        
        # Initially state file doesn't exist
        self.assertFalse(os.path.exists(self.state_file))
        
        with patch('builtins.print'):
            orchestrator(self.args)
        
        # After orchestrator runs, state file should exist
        self.assertTrue(os.path.exists(self.state_file))

    @patch('vibe_coding.utils.ai_call')
    def test_state_file_is_valid_json(self, mock_ai):
        """Test that state file contains valid JSON"""
        mock_ai.return_value = "Summary."
        
        with patch('builtins.print'):
            orchestrator(self.args)
        
        # Try to load the state file as JSON
        with open(self.state_file, "r") as f:
            state = json.load(f)
        
        # Should be a valid dict
        self.assertIsInstance(state, dict)
        self.assertIn("summarize", state)

    @patch('vibe_coding.utils.ai_call')
    def test_state_tracks_multiple_runs(self, mock_ai):
        """Test that state is updated across multiple runs"""
        mock_ai.return_value = "Summary 1."
        
        with patch('builtins.print'):
            orchestrator(self.args)
        
        state1 = load_state()
        self.assertEqual(state1["summarize"], "Summary 1.")
        
        # Change the mock and run again
        mock_ai.return_value = "Summary 2."
        
        with patch('builtins.print'):
            orchestrator(self.args)
        
        state2 = load_state()
        self.assertEqual(state2["summarize"], "Summary 2.")


if __name__ == "__main__":
    unittest.main()
