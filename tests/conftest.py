"""
Pytest configuration and shared fixtures for WhatsApp Group Manager tests.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from dotenv import load_dotenv

# Add src to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Load environment variables for testing
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)


@pytest.fixture(scope="session")
def project_root():
    """Returns the project root directory path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session") 
def test_data_dir():
    """Returns the test data directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_group_data():
    """Sample group data for testing."""
    return {
        "id": "120363295648424210@g.us",
        "subject": "Test Group",
        "subjectOwner": "5511999999999@s.whatsapp.net",
        "subjectTime": 1714769954,
        "pictureUrl": None,
        "size": 10,
        "creation": 1714769954,
        "owner": "5511999999999@s.whatsapp.net",
        "desc": "Test group description",
        "descId": "BAE57E16498982ED",
        "restrict": False,
        "announce": False
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "id": "message_123",
        "messageType": "conversation",
        "conversation": "Hello, this is a test message",
        "from": "5511999999999@s.whatsapp.net",
        "timestamp": 1234567890,
        "pushName": "Test User"
    }


@pytest.fixture
def mock_evolution_api_response():
    """Mock Evolution API response data."""
    return {
        "status": "success",
        "version": "2.2.3",
        "instance": {
            "instanceName": "TestInstance",
            "status": "open"
        }
    }


@pytest.fixture
def mock_groups_response(sample_group_data):
    """Mock groups API response."""
    return [sample_group_data]


@pytest.fixture
def mock_messages_response(sample_message_data):
    """Mock messages API response."""
    return {
        "messages": {
            "records": [sample_message_data]
        }
    }


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API testing."""
    with pytest.MonkeyPatch().context() as m:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_get = Mock(return_value=mock_response)
        m.setattr("requests.get", mock_get)
        yield mock_get


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    return {
        "EVO_BASE_URL": "http://localhost:8081",
        "EVO_API_TOKEN": "test_api_token",
        "EVO_INSTANCE_NAME": "TestInstance",
        "EVO_INSTANCE_TOKEN": "test_instance_token",
        "WHATSAPP_NUMBER": "5511999999999"
    }


@pytest.fixture
def temp_csv_file(tmp_path, sample_group_data):
    """Creates a temporary CSV file with sample group data."""
    csv_content = """group_id,name,enabled,horario,is_names,is_links,min_messages_summary,send_to_group,send_to_personal,script_path
120363295648424210@g.us,Test Group,true,22:00,true,false,5,true,false,src/whatsapp_manager/core/summary.py"""
    
    csv_file = tmp_path / "test_groups.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)


@pytest.fixture
def mock_group_controller():
    """Mock GroupController for testing."""
    mock_controller = Mock()
    mock_controller.fetch_groups.return_value = []
    mock_controller.check_api_availability.return_value = {
        "available": True,
        "message": "API is available",
        "response_time_ms": 100
    }
    mock_controller.check_whatsapp_connection.return_value = {
        "connected": True,
        "state": "open",
        "message": "WhatsApp connected successfully",
        "level": "info"
    }
    return mock_controller


@pytest.fixture(autouse=True)
def cleanup_imports():
    """Cleanup imported modules after each test to avoid import conflicts."""
    yield
    # Remove any whatsapp_manager modules from sys.modules to ensure clean imports
    modules_to_remove = [mod for mod in sys.modules.keys() if mod.startswith('whatsapp_manager')]
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]


# Pytest hooks for custom functionality

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "functional: mark test as functional test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API connectivity"
    )
    config.addinivalue_line(
        "markers", "offline: mark test as working offline"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.api)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.offline)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup function called before each test."""
    # Skip API tests if environment variables are not set
    if item.get_closest_marker("api"):
        required_env_vars = ["EVO_BASE_URL", "EVO_API_TOKEN", "EVO_INSTANCE_NAME"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print(f"\n🧪 Starting test session with Python {sys.version}")
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"🔧 Source directory: {SRC_DIR}")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    if exitstatus == 0:
        print("\n✅ All tests completed successfully!")
    else:
        print(f"\n❌ Tests finished with exit status: {exitstatus}")
