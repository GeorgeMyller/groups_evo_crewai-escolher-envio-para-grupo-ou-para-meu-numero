# 🧪 Test Suite - WhatsApp Group Manager

This directory contains comprehensive tests for the WhatsApp Group Manager system, organized by test type for better maintainability and clarity.

## 📁 Test Structure

```
tests/
├── README.md                    # This file - Test documentation
├── conftest.py                  # Pytest configuration and fixtures
├── pytest.ini                  # Pytest settings
├── unit/                        # Unit tests (individual components)
├── integration/                 # Integration tests (component interactions)
├── functional/                  # Functional tests (feature-level testing)
├── e2e/                        # End-to-end tests (full workflow testing)
└── fixtures/                   # Test data and fixtures
```

## 🎯 Test Categories

### 🔧 Integration Tests (`integration/`)
Tests that verify the interaction between system components and external services:

- **`test_api_connectivity.py`** - Complete Evolution API connectivity tests
- **`test_api_detailed.py`** - Detailed API error diagnosis
- **`test_alternative_urls.py`** - Alternative API URL discovery
- **`test_whatsapp_status.py`** - WhatsApp connection status verification

### ⚙️ Functional Tests (`functional/`)
Tests that verify specific system functionalities and features:

- **`test_imports_and_functionality.py`** - Module imports and basic functionality
- **`test_structure.py`** - Codebase structure validation
- **`test_offline_mode.py`** - Offline mode functionality

### 🧩 Unit Tests (`unit/`)
Tests for individual components in isolation:
- *Coming soon* - Individual service and model tests

### 🔄 End-to-End Tests (`e2e/`)
Tests that verify complete user workflows:
- *Coming soon* - Full summary generation workflows

## 🚀 Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Ensure environment is configured
cp .env.example .env
# Edit .env with your settings
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/whatsapp_manager

# Run with verbose output
pytest -v
```

### Run Specific Test Categories

```bash
# Integration tests only
pytest tests/integration/

# Functional tests only
pytest tests/functional/

# Unit tests only
pytest tests/unit/

# End-to-end tests only
pytest tests/e2e/
```

### Run Individual Tests

```bash
# API connectivity
pytest tests/integration/test_api_connectivity.py

# Structure validation
pytest tests/functional/test_structure.py

# Offline mode
pytest tests/functional/test_offline_mode.py
```

## 🔧 Test Configuration

### Environment Variables for Testing

```bash
# Required for API tests
EVO_BASE_URL=http://your-evolution-api-url:port
EVO_API_TOKEN=your_api_token
EVO_INSTANCE_NAME=your_instance_name
EVO_INSTANCE_TOKEN=your_instance_token

# Optional for comprehensive testing
WHATSAPP_NUMBER=your_whatsapp_number
OPENAI_API_KEY=your_openai_key
```

### Test Modes

1. **Online Mode** - Tests with real API connections
   - Requires Evolution API to be running
   - Tests full integration capabilities

2. **Offline Mode** - Tests without external dependencies
   - Uses mock data and cached responses
   - Suitable for CI/CD environments

## 📊 Test Coverage

Current test coverage focuses on:
- ✅ API connectivity and error handling
- ✅ Module imports and structure validation
- ✅ Offline mode functionality
- ✅ WhatsApp connection status
- 🔄 Unit tests (in development)
- 🔄 End-to-end workflows (in development)

### Coverage Goals

- **Unit Tests**: 80%+ coverage of core business logic
- **Integration Tests**: All external API interactions
- **Functional Tests**: All user-facing features
- **E2E Tests**: Critical user workflows

## 🐛 Debugging Tests

### Common Issues

1. **API Connection Failures**
   ```bash
   # Test API connectivity first
   pytest tests/integration/test_api_connectivity.py -v
   ```

2. **Import Errors**
   ```bash
   # Validate structure and imports
   pytest tests/functional/test_structure.py -v
   ```

3. **Environment Issues**
   ```bash
   # Check environment loading
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print([k for k in os.environ.keys() if 'EVO_' in k])"
   ```

### Debug Mode

```bash
# Run tests with debug output
pytest --log-cli-level=DEBUG tests/

# Run with Python debugger
pytest --pdb tests/failing_test.py
```

## 📝 Writing New Tests

### Test Naming Convention

- `test_<component>_<functionality>.py` for files
- `test_<specific_behavior>()` for functions
- Use descriptive names that explain what is being tested

### Test Structure

```python
def test_should_return_groups_when_api_available():
    """Test that groups are returned when API is available"""
    # Arrange
    controller = GroupController()
    
    # Act
    groups = controller.get_groups()
    
    # Assert
    assert isinstance(groups, list)
    assert len(groups) >= 0
```

### Test Categories Guidelines

- **Unit**: Test single function/method in isolation
- **Integration**: Test interaction between 2+ components
- **Functional**: Test complete feature from user perspective
- **E2E**: Test complete user journey/workflow

## 📚 Test Documentation

Individual test files contain:
- Purpose and scope description
- Setup requirements
- Expected outcomes
- Error scenarios covered

For detailed test cases and scenarios, see:
- [Message Processing Test Cases](test_message_sandeco_conceptual.md)

## 🔄 Continuous Integration

Tests are designed to run in CI/CD environments:
- Offline mode for environments without API access
- Mock data for reliable test execution
- Clear pass/fail criteria
- Detailed error reporting

---

*For questions about testing or to report test issues, please open an issue on GitHub.*
