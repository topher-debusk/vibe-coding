"""
Tests for the vibe_coding package

This directory contains unit and integration tests for the vibe coding agent.

## Test Files

### test_tools.py
Tests for the tools in `vibe_coding/tools/`:
- `TestSummarizeTool`: Tests for summarize_text function
  - ai_call is mocked to prevent real API requests
  - Verifies tool registration and metadata
  - Tests input/output handling
  
- `TestTodoTool`: Tests for generate_todos function
  - Tests text parsing and formatting
  - Verifies whitespace handling
  - Tests edge cases (empty input, no periods, etc.)
  
- `TestToolsIntegration`: Integration tests for tools working together

### test_orchestrator.py
Tests for `vibe_coding/orchestrator.py`:
- `TestOrchestrator`: Core orchestrator functionality
  - Verifies tools run in correct sequence
  - Tests state updates
  - Validates output chaining (summarize -> todo)
  - Tests error handling for missing files
  - Verifies tool registry access

- `TestOrchestratorStateManagement`: State file handling
  - Tests state persistence
  - Validates JSON format
  - Tests state across multiple runs

## Running Tests

### Using unittest (recommended)
```bash
# From workspace root
python3 -m unittest discover vibe_coding/tests

# Verbose output
python3 -m unittest discover vibe_coding/tests -v

# Specific test file
python3 -m unittest vibe_coding.tests.test_tools

# Specific test class
python3 -m unittest vibe_coding.tests.test_tools.TestSummarizeTool

# Specific test method
python3 -m unittest vibe_coding.tests.test_tools.TestSummarizeTool.test_summarize_text_calls_ai
```

### Using pytest (if installed)
```bash
pytest vibe_coding/tests/ -v
pytest vibe_coding/tests/test_tools.py -v
pytest vibe_coding/tests/test_orchestrator.py::TestOrchestrator -v
```

## Test Design

### Mocking Strategy
- `ai_call()` is mocked to prevent real OpenAI API calls
- State files use temporary directories to avoid conflicts
- File I/O is tested with temporary files in isolated directories

### Setup/Teardown
- Each test class has setUp() to create fixtures
- tearDown() cleans up temporary files and patches
- State patches are properly started and stopped

### Coverage
- Tools are tested both in isolation and integration
- State management handles persistence correctly
- Orchestrator verifies tool sequencing and data flow
- Edge cases and error conditions are covered
"""
