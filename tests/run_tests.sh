#!/bin/bash
"""
Test Runner Script for WhatsApp Group Manager
Executes different categories of tests with proper configuration.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if pytest is installed
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        print_error "pytest is not installed. Installing..."
        pip install pytest pytest-cov pytest-mock
    fi
}

# Function to check environment
check_environment() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Some tests may fail."
        print_warning "Copy .env.example to .env and configure your settings."
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    pytest tests/ -v --tb=short
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    pytest tests/integration/ -v --tb=short -m integration
}

# Function to run functional tests
run_functional_tests() {
    print_status "Running functional tests..."
    pytest tests/functional/ -v --tb=short -m functional
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    pytest tests/unit/ -v --tb=short -m unit
}

# Function to run offline tests only
run_offline_tests() {
    print_status "Running offline tests only..."
    pytest tests/ -v --tb=short -m "offline"
}

# Function to run API tests only
run_api_tests() {
    print_status "Running API tests only..."
    pytest tests/ -v --tb=short -m "api"
}

# Function to run with coverage
run_with_coverage() {
    print_status "Running tests with coverage..."
    pytest tests/ --cov=src/whatsapp_manager --cov-report=html --cov-report=term-missing -v
    print_success "Coverage report generated in htmlcov/"
}

# Function to run quick tests (fast tests only)
run_quick_tests() {
    print_status "Running quick tests (excluding slow tests)..."
    pytest tests/ -v --tb=short -m "not slow"
}

# Function to run smoke tests (basic functionality)
run_smoke_tests() {
    print_status "Running smoke tests..."
    pytest tests/functional/test_imports_and_functionality.py tests/functional/test_structure.py -v
}

# Function to validate test structure
validate_test_structure() {
    print_status "Validating test structure..."
    
    # Check if test directories exist
    for dir in "unit" "integration" "functional" "e2e" "fixtures"; do
        if [ ! -d "tests/$dir" ]; then
            print_error "Missing test directory: tests/$dir"
            exit 1
        fi
    done
    
    # Check if configuration files exist
    if [ ! -f "tests/pytest.ini" ]; then
        print_error "Missing pytest.ini configuration"
        exit 1
    fi
    
    if [ ! -f "tests/conftest.py" ]; then
        print_error "Missing conftest.py configuration"
        exit 1
    fi
    
    print_success "Test structure is valid"
}

# Function to show help
show_help() {
    echo "WhatsApp Group Manager Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  all               Run all tests"
    echo "  integration       Run integration tests only"
    echo "  functional        Run functional tests only"
    echo "  unit              Run unit tests only"
    echo "  offline           Run offline tests only"
    echo "  api               Run API tests only"
    echo "  coverage          Run tests with coverage report"
    echo "  quick             Run quick tests (exclude slow tests)"
    echo "  smoke             Run smoke tests (basic functionality)"
    echo "  validate          Validate test structure"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all                    # Run all tests"
    echo "  $0 offline                # Run only offline tests"
    echo "  $0 coverage               # Run with coverage"
    echo "  $0 smoke                  # Quick validation"
}

# Main script logic
main() {
    print_status "WhatsApp Group Manager Test Runner"
    print_status "Project: $PROJECT_ROOT"
    
    # Initial checks
    check_pytest
    check_environment
    
    # Parse command line argument
    case "${1:-all}" in
        "all")
            run_all_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "functional")
            run_functional_tests
            ;;
        "unit")
            run_unit_tests
            ;;
        "offline")
            run_offline_tests
            ;;
        "api")
            run_api_tests
            ;;
        "coverage")
            run_with_coverage
            ;;
        "quick")
            run_quick_tests
            ;;
        "smoke")
            run_smoke_tests
            ;;
        "validate")
            validate_test_structure
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    print_success "Test execution completed!"
}

# Run main function
main "$@"
