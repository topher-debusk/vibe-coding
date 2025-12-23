"""Tests for tools: summarize.py and todo.py"""
import unittest
from unittest.mock import patch, MagicMock
from vibe_coding.tools.summarize import summarize_text
from vibe_coding.tools.todo import generate_todos
from vibe_coding.utils import TOOLS


class TestSummarizeTool(unittest.TestCase):
    """Tests for the summarize tool"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_text = "This is a sample text. It has multiple sentences. And it should be summarized."

    def tearDown(self):
        """Clean up after tests"""
        pass

    @patch('vibe_coding.utils.ai_call')
    def test_summarize_text_calls_ai(self, mock_ai):
        """Test that summarize_text calls ai_call with input text"""
        mock_ai.return_value = "Summary of the text."
        
        result = summarize_text(self.test_text)
        
        mock_ai.assert_called_once_with(self.test_text)
        self.assertEqual(result, "Summary of the text.")

    @patch('vibe_coding.utils.ai_call')
    def test_summarize_text_returns_ai_response(self, mock_ai):
        """Test that summarize_text returns the AI response"""
        expected_summary = "This is a concise summary."
        mock_ai.return_value = expected_summary
        
        result = summarize_text(self.test_text)
        
        self.assertEqual(result, expected_summary)

    @patch('vibe_coding.utils.ai_call')
    def test_summarize_text_with_empty_string(self, mock_ai):
        """Test summarize_text with empty input"""
        mock_ai.return_value = ""
        
        result = summarize_text("")
        
        mock_ai.assert_called_once_with("")
        self.assertEqual(result, "")

    def test_summarize_tool_registered(self):
        """Test that summarize tool is registered in TOOLS"""
        self.assertIn("summarize", TOOLS)
        self.assertIn("fn", TOOLS["summarize"])
        self.assertIn("description", TOOLS["summarize"])

    def test_summarize_tool_metadata(self):
        """Test that summarize tool has correct metadata"""
        tool = TOOLS["summarize"]
        self.assertEqual(tool["description"], "Summarize input text into a short summary")
        self.assertEqual(tool["inputs"], ["text"])
        self.assertEqual(tool["outputs"], ["summary"])


class TestTodoTool(unittest.TestCase):
    """Tests for the todo tool"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_text = "First task. Second task. Third task."

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_generate_todos_basic(self):
        """Test basic todo generation"""
        result = generate_todos(self.test_text)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "- First task")
        self.assertEqual(result[1], "- Second task")
        self.assertEqual(result[2], "- Third task")

    def test_generate_todos_with_empty_string(self):
        """Test generate_todos with empty input"""
        result = generate_todos("")
        
        self.assertEqual(result, [])

    def test_generate_todos_single_task(self):
        """Test generate_todos with single task"""
        result = generate_todos("Single task.")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "- Single task")

    def test_generate_todos_no_period(self):
        """Test generate_todos when text has no periods"""
        result = generate_todos("No periods here")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "- No periods here")

    def test_generate_todos_multiple_periods(self):
        """Test generate_todos with multiple consecutive periods"""
        result = generate_todos("Task one. . Task two.")
        
        # Empty strings from consecutive periods are filtered out
        self.assertTrue(len(result) >= 2)
        self.assertEqual(result[0], "- Task one")

    def test_generate_todos_with_whitespace(self):
        """Test generate_todos strips whitespace from tasks"""
        result = generate_todos("  Task one  .  Task two  .")
        
        self.assertEqual(result[0], "- Task one")
        self.assertEqual(result[1], "- Task two")

    def test_todo_tool_registered(self):
        """Test that todo tool is registered in TOOLS"""
        self.assertIn("todo", TOOLS)
        self.assertIn("fn", TOOLS["todo"])
        self.assertIn("description", TOOLS["todo"])

    def test_todo_tool_metadata(self):
        """Test that todo tool has correct metadata"""
        tool = TOOLS["todo"]
        self.assertEqual(tool["description"], "Generate a todo list from text")
        self.assertEqual(tool["inputs"], ["text"])
        self.assertEqual(tool["outputs"], ["todos"])


class TestToolsIntegration(unittest.TestCase):
    """Integration tests for tools"""

    @patch('vibe_coding.utils.ai_call')
    def test_both_tools_together(self, mock_ai):
        """Test using both tools in sequence"""
        mock_ai.return_value = "Summary of the tasks."
        
        text = "Task one. Task two. Task three."
        
        # Summarize first
        summary = summarize_text(text)
        self.assertEqual(summary, "Summary of the tasks.")
        
        # Then generate todos
        todos = generate_todos(text)
        self.assertEqual(len(todos), 3)


if __name__ == "__main__":
    unittest.main()
