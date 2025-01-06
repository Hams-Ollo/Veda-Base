"""Test runner script for the multi-agent system."""

import os
import sys
import pytest
import coverage
import asyncio
from pathlib import Path

def run_tests_with_coverage():
    """Run all tests with coverage reporting."""
    # Initialize coverage.py
    cov = coverage.Coverage(
        branch=True,
        source=['app'],
        omit=[
            '*/tests/*',
            '*/migrations/*',
            '*/site-packages/*',
            '*/__init__.py'
        ]
    )

    # Start coverage collection
    cov.start()

    try:
        # Run pytest with asyncio
        pytest_args = [
            '-v',  # Verbose output
            '--asyncio-mode=auto',  # Handle async tests
            '--tb=short',  # Shorter traceback format
            'tests',  # Test directory
            '-p', 'no:warnings'  # Disable warning capture
        ]
        
        # Add coverage options
        pytest_args.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:coverage_html'
        ])

        # Run the tests
        result = pytest.main(pytest_args)

        # Stop coverage collection
        cov.stop()
        cov.save()

        # Generate coverage reports
        print("\nGenerating coverage reports...")
        cov.report(show_missing=True)
        cov.html_report(directory='coverage_html')

        return result

    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        return 1

    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1

    finally:
        # Clean up coverage
        cov.stop()
        try:
            cov.save()
        except coverage.misc.CoverageException:
            pass

def main():
    """Main entry point for the test runner."""
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Create directories for reports if they don't exist
    os.makedirs('coverage_html', exist_ok=True)

    print("Starting test run with coverage...")
    result = run_tests_with_coverage()

    # Print summary
    print("\nTest Run Summary:")
    print("-" * 40)
    print(f"Exit Code: {result}")
    print(f"Coverage Report: {os.path.join(project_root, 'coverage_html', 'index.html')}")

    # Return appropriate exit code
    sys.exit(result)

if __name__ == '__main__':
    main() 