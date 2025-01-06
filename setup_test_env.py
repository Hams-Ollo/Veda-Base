"""Script to set up the test environment for the multi-agent system."""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment(venv_path):
    """Create a virtual environment for testing."""
    print(f"Creating virtual environment at {venv_path}...")
    venv.create(venv_path, with_pip=True)

def get_python_executable(venv_path):
    """Get the Python executable path for the virtual environment."""
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    return str(python_path)

def install_dependencies(python_path):
    """Install test dependencies using pip."""
    print("Installing test dependencies...")
    
    # Upgrade pip first
    subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install test requirements
    subprocess.run([
        python_path, "-m", "pip", "install", "-r", "test-requirements.txt"
    ], check=True)
    
    # Install project in editable mode
    subprocess.run([
        python_path, "-m", "pip", "install", "-e", "."
    ], check=True)

def create_test_directories():
    """Create necessary directories for test artifacts."""
    directories = [
        "tests/test_data",
        "coverage_html",
        "test-reports",
        "test-reports/assets",
        ".pytest_cache"
    ]
    
    print("Creating test directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def setup_test_data():
    """Set up test data and fixtures."""
    test_data_dir = Path("tests/test_data")
    
    # Create sample test files
    print("Setting up test data...")
    
    # Sample document for testing
    sample_doc = test_data_dir / "sample_document.txt"
    if not sample_doc.exists():
        with open(sample_doc, "w") as f:
            f.write("This is a sample document for testing.\n")
            f.write("It contains multiple lines of text.\n")
            f.write("Used for testing document processing capabilities.\n")
    
    # Sample image for testing
    sample_image = test_data_dir / "sample_image.txt"
    if not sample_image.exists():
        with open(sample_image, "w") as f:
            f.write("[Sample image data for testing]\n")
    
    # Sample audio for testing
    sample_audio = test_data_dir / "sample_audio.txt"
    if not sample_audio.exists():
        with open(sample_audio, "w") as f:
            f.write("[Sample audio data for testing]\n")
    
    # Sample video for testing
    sample_video = test_data_dir / "sample_video.txt"
    if not sample_video.exists():
        with open(sample_video, "w") as f:
            f.write("[Sample video data for testing]\n")

def verify_setup():
    """Verify that the test environment is set up correctly."""
    print("Verifying test environment setup...")
    
    # Check virtual environment
    if not os.path.exists(".venv"):
        raise RuntimeError("Virtual environment not created successfully")
    
    # Check test directories
    required_dirs = [
        "tests/test_data",
        "coverage_html",
        "test-reports",
        ".pytest_cache"
    ]
    for directory in required_dirs:
        if not os.path.exists(directory):
            raise RuntimeError(f"Required directory {directory} not created")
    
    # Check test data
    required_files = [
        "tests/test_data/sample_document.txt",
        "tests/test_data/sample_image.txt",
        "tests/test_data/sample_audio.txt",
        "tests/test_data/sample_video.txt"
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise RuntimeError(f"Required test file {file} not created")
    
    print("Test environment setup verified successfully!")

def main():
    """Main entry point for setting up the test environment."""
    try:
        # Ensure we're in the project root directory
        project_root = Path(__file__).parent
        os.chdir(project_root)
        
        # Create virtual environment
        venv_path = project_root / ".venv"
        if not venv_path.exists():
            create_virtual_environment(venv_path)
        
        # Get Python executable path
        python_path = get_python_executable(venv_path)
        
        # Install dependencies
        install_dependencies(python_path)
        
        # Create test directories
        create_test_directories()
        
        # Set up test data
        setup_test_data()
        
        # Verify setup
        verify_setup()
        
        print("\nTest environment setup completed successfully!")
        print("\nTo activate the virtual environment:")
        if sys.platform == "win32":
            print(f"    {venv_path}\\Scripts\\activate")
        else:
            print(f"    source {venv_path}/bin/activate")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\nError running command: {e.cmd}")
        print(f"Exit code: {e.returncode}")
        return 1
        
    except Exception as e:
        print(f"\nError setting up test environment: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 