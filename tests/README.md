# Newtone Translation System - Test Suite

This directory contains comprehensive tests for the Newtone Translation System, organized by test type and architectural layer.

## 📁 Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_runner.py             # Convenient test runner script
├── unit/                      # Unit tests for individual components
│   ├── test_domain_models.py
│   ├── test_placeholder_manager.py
│   ├── test_content_processor.py
│   ├── test_infrastructure_providers.py
│   ├── test_infrastructure_storage.py
│   └── test_application_services.py
├── integration/               # Integration tests for full workflows
│   └── test_translation_workflow.py
└── fixtures/                  # Test data and utilities
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation with mocked dependencies:

- **Domain Layer Tests**: Pure business logic without external dependencies
  - `test_domain_models.py` - Data models and validation
  - `test_placeholder_manager.py` - Content protection logic
  - `test_content_processor.py` - Format-specific processing

- **Infrastructure Layer Tests**: External service integrations
  - `test_infrastructure_providers.py` - Translation providers (OpenAI, Mock)
  - `test_infrastructure_storage.py` - File storage operations

- **Application Layer Tests**: Workflow orchestration
  - `test_application_services.py` - Service coordination and configuration

### Integration Tests (`tests/integration/`)

Test complete workflows across multiple layers:

- **Full Translation Workflows**: End-to-end translation processes
- **CLI Integration**: Command-line interface testing
- **Provider Integration**: Real/mocked external service interactions

## 🚀 Running Tests

### Using the Test Runner Script

```bash
# Run all tests
python tests/test_runner.py

# Run with coverage
python tests/test_runner.py --coverage

# Run only unit tests
python tests/test_runner.py --unit

# Run only integration tests
python tests/test_runner.py --integration

# Run specific test file
python tests/test_runner.py --test tests/unit/test_domain_models.py

# Run with verbose output
python tests/test_runner.py --verbose

# Run linting
python tests/test_runner.py --lint

# Run code formatting
python tests/test_runner.py --format
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/newtone_translate --cov-report=term-missing --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_domain_models.py

# Run specific test method
pytest tests/unit/test_domain_models.py::TestTranslationRequest::test_valid_request_creation

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_translate"
```

## 🔧 Test Configuration

### Pytest Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src/newtone_translate --cov-report=term-missing"
```

### Fixtures (`conftest.py`)

Shared test fixtures provide:
- Sample content in various formats (HTML, Markdown, Text)
- Mock configuration files and directories
- Brand guidelines, glossaries, and DNT terms
- Mock API responses
- Temporary file systems

## 📊 Coverage Goals

Target coverage levels:
- **Domain Layer**: 95%+ (pure business logic)
- **Application Layer**: 90%+ (workflow orchestration)
- **Infrastructure Layer**: 85%+ (external integrations)
- **Overall**: 90%+

## 🎯 Testing Best Practices

### Unit Tests

1. **Test in Isolation**: Mock all external dependencies
2. **Test Business Logic**: Focus on domain rules and behavior
3. **Test Edge Cases**: Empty inputs, invalid data, boundary conditions
4. **Test Error Handling**: Exception scenarios and validation

### Integration Tests

1. **Test Real Workflows**: End-to-end user scenarios
2. **Test Component Interaction**: How layers work together
3. **Test Configuration**: Real config files and settings
4. **Test External Services**: With mocked but realistic responses

### Test Data

1. **Use Realistic Data**: Real-world content examples
2. **Test Multiple Formats**: HTML, Markdown, plain text
3. **Test Multiple Languages**: Various target languages
4. **Test Edge Cases**: Special characters, empty content, large files

## 🔍 Debugging Tests

### Running Specific Tests

```bash
# Debug single test with print statements
pytest tests/unit/test_domain_models.py::TestTranslationRequest::test_valid_request_creation -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest --pdb -x
```

### Coverage Analysis

```bash
# Generate HTML coverage report
pytest --cov=src/newtone_translate --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 🚨 Continuous Integration

### Pre-commit Checks

Before committing code, run:

```bash
# Format code
python tests/test_runner.py --format

# Run linting
python tests/test_runner.py --lint

# Run all tests with coverage
python tests/test_runner.py --coverage
```

### GitHub Actions (Future)

Automated testing pipeline:
1. Run linting and formatting checks
2. Run unit tests with coverage
3. Run integration tests
4. Generate coverage reports
5. Quality gates for pull requests

## 📝 Writing New Tests

### Domain Layer Test Example

```python
def test_new_domain_feature(self):
    """Test new domain functionality."""
    # Arrange
    domain_object = DomainClass()
    
    # Act
    result = domain_object.do_something("input")
    
    # Assert
    assert result == "expected_output"
```

### Integration Test Example

```python
def test_new_workflow_integration(self):
    """Test new workflow end-to-end."""
    # Arrange
    request = TranslationRequest(text="test", target_lang="fr")
    
    # Act
    with patch.dict(os.environ, {}, clear=True):  # Use mock provider
        result = service.translate(request)
    
    # Assert
    assert result.translated_text is not None
    assert "[MOCK FR]" in result.translated_text
```

## 🏆 Test Quality Metrics

Monitor test quality with:
- **Coverage Percentage**: Aim for 90%+
- **Test Execution Time**: Keep under 30 seconds for full suite
- **Test Reliability**: No flaky tests
- **Test Maintainability**: Clear, readable test code

---

**Happy Testing! 🧪**
