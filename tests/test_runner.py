#!/usr/bin/env python3
"""
Test runner script for Newtone Translation System.

Provides convenient ways to run different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def run_unit_tests(coverage=False, verbose=False):
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    if coverage:
        cmd.extend(["--cov=src/newtone_translate", "--cov-report=term-missing", "--cov-report=html"])
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "tests/integration/"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Integration Tests")


def run_all_tests(coverage=False, verbose=False):
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if coverage:
        cmd.extend(["--cov=src/newtone_translate", "--cov-report=term-missing", "--cov-report=html"])
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "All Tests")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test."""
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Specific Test: {test_path}")


def run_linting():
    """Run code linting."""
    commands = [
        (["python", "-m", "flake8", "src/", "tests/"], "Flake8 Linting"),
        (["python", "-m", "black", "--check", "src/", "tests/"], "Black Code Formatting Check"),
        (["python", "-m", "mypy", "src/newtone_translate/"], "MyPy Type Checking"),
    ]
    
    all_passed = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            all_passed = False
    
    return all_passed


def run_formatting():
    """Run code formatting."""
    cmd = ["python", "-m", "black", "src/", "tests/"]
    return run_command(cmd, "Black Code Formatting")


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Newtone Translation System Test Runner")
    parser.add_argument("--coverage", "-c", action="store_true", help="Include coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--format", action="store_true", help="Run code formatting")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--test", type=str, help="Run specific test file or test")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if project_root.exists():
        import os
        os.chdir(project_root)
    
    success = True
    
    if args.lint:
        success = run_linting()
    elif args.format:
        success = run_formatting()
    elif args.unit:
        success = run_unit_tests(coverage=args.coverage, verbose=args.verbose)
    elif args.integration:
        success = run_integration_tests(verbose=args.verbose)
    elif args.test:
        success = run_specific_test(args.test, verbose=args.verbose)
    else:
        # Default: run all tests
        success = run_all_tests(coverage=args.coverage, verbose=args.verbose)
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
