"""Script to clean up test artifacts and reset the test environment."""

import os
import sys
import shutil
from pathlib import Path

def remove_test_artifacts():
    """Remove test artifacts and generated files."""
    artifacts = [
        ".coverage",
        "coverage_html",
        "test-reports",
        ".pytest_cache",
        "tests/__pycache__",
        "tests/test_data",
        "tests/*.pyc",
        "tests/**/*.pyc",
        "tests/**/__pycache__",
        "htmlcov",
        ".tox",
        "*.egg-info",
        "dist",
        "build",
        ".eggs"
    ]

    print("Removing test artifacts...")
    for artifact in artifacts:
        paths = Path(".").glob(artifact)
        for path in paths:
            try:
                if path.is_file():
                    path.unlink()
                    print(f"Removed file: {path}")
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path}")
            except Exception as e:
                print(f"Error removing {path}: {e}")

def remove_virtual_environment():
    """Remove the virtual environment."""
    venv_path = Path(".venv")
    if venv_path.exists():
        print("Removing virtual environment...")
        try:
            shutil.rmtree(venv_path)
            print("Virtual environment removed successfully")
        except Exception as e:
            print(f"Error removing virtual environment: {e}")

def clean_python_cache():
    """Clean Python cache files recursively."""
    print("Cleaning Python cache files...")
    
    # Remove .pyc files
    for pyc in Path(".").rglob("*.pyc"):
        try:
            pyc.unlink()
            print(f"Removed: {pyc}")
        except Exception as e:
            print(f"Error removing {pyc}: {e}")
    
    # Remove __pycache__ directories
    for cache_dir in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(cache_dir)
            print(f"Removed: {cache_dir}")
        except Exception as e:
            print(f"Error removing {cache_dir}: {e}")

def reset_test_data():
    """Reset test data to initial state."""
    test_data_dir = Path("tests/test_data")
    if test_data_dir.exists():
        print("Resetting test data...")
        try:
            shutil.rmtree(test_data_dir)
            print("Test data directory removed")
        except Exception as e:
            print(f"Error resetting test data: {e}")

def verify_cleanup():
    """Verify that cleanup was successful."""
    print("\nVerifying cleanup...")
    
    artifacts_to_check = [
        ".coverage",
        "coverage_html",
        "test-reports",
        ".pytest_cache",
        "tests/__pycache__",
        "tests/test_data",
        ".venv"
    ]
    
    all_removed = True
    for artifact in artifacts_to_check:
        path = Path(artifact)
        if path.exists():
            print(f"Warning: {artifact} still exists")
            all_removed = False
    
    if all_removed:
        print("All test artifacts removed successfully!")
    else:
        print("\nSome artifacts could not be removed. Please check and remove them manually.")

def main():
    """Main entry point for cleaning up the test environment."""
    try:
        # Ensure we're in the project root directory
        project_root = Path(__file__).parent
        os.chdir(project_root)
        
        # Ask for confirmation
        response = input("This will remove all test artifacts and the virtual environment. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cleanup cancelled")
            return 0
        
        print("\nStarting cleanup process...")
        
        # Remove test artifacts
        remove_test_artifacts()
        
        # Clean Python cache
        clean_python_cache()
        
        # Reset test data
        reset_test_data()
        
        # Remove virtual environment
        remove_virtual_environment()
        
        # Verify cleanup
        verify_cleanup()
        
        print("\nCleanup completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nError during cleanup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 