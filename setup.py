#!/usr/bin/env python3
"""
Setup script for KiCad Library Manager.
Handles virtual environment creation, dependency installation, and initial configuration.
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path


def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print('='*60)


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message):
    """Print an informational message."""
    print(f"ℹ {message}")


def check_python_version():
    """
    Check if the Python version meets minimum requirements.
    
    Returns:
        bool: True if version is sufficient, False otherwise
    """
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print_error(f"Python {min_version[0]}.{min_version[1]} or higher is required")
        print_error(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print_success(f"Python {current_version[0]}.{current_version[1]} detected")
    return True


def get_project_root():
    """
    Get the root directory of the project.
    
    Returns:
        Path: Absolute path to project root
    """
    return Path(__file__).parent.resolve()


def create_virtual_environment():
    """
    Create a virtual environment for the project.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step("Creating virtual environment")
    
    project_root = get_project_root()
    venv_path = project_root / "venv"
    
    if venv_path.exists():
        print_info(f"Virtual environment already exists at {venv_path}")
        response = input("Recreate it? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print_success("Using existing virtual environment")
            return True
        
        # Remove existing venv
        import shutil
        print_info("Removing existing virtual environment...")
        shutil.rmtree(venv_path)
    
    try:
        print_info(f"Creating virtual environment at {venv_path}...")
        subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            check=True
        )
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """
    Get the path to the Python interpreter in the virtual environment.
    
    Returns:
        Path: Path to venv Python executable
    """
    project_root = get_project_root()
    venv_path = project_root / "venv"
    
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_venv_pip():
    """
    Get the path to pip in the virtual environment.
    
    Returns:
        Path: Path to venv pip executable
    """
    project_root = get_project_root()
    venv_path = project_root / "venv"
    
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def install_dependencies():
    """
    Install required dependencies in the virtual environment.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step("Installing dependencies")
    
    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"
    pip_path = get_venv_pip()
    
    if not requirements_file.exists():
        print_error(f"requirements.txt not found at {requirements_file}")
        return False
    
    try:
        # Upgrade pip first
        print_info("Upgrading pip...")
        subprocess.run(
            [str(pip_path), 'install', '--upgrade', 'pip'],
            check=True,
            capture_output=True
        )
        
        # Install requirements
        print_info("Installing packages from requirements.txt...")
        subprocess.run(
            [str(pip_path), 'install', '-r', str(requirements_file)],
            check=True
        )
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def create_config_file():
    """
    Create the initial configuration file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step("Creating configuration file")
    
    project_root = get_project_root()
    config_path = project_root / "config.json"
    
    if config_path.exists():
        print_info("Configuration file already exists")
        response = input("Overwrite it? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print_success("Keeping existing configuration")
            return True
    
    # Default configuration
    config = {
        "library_path": "library",
        "debug_mode": False,
        "easyeda2kicad_path": None
    }
    
    # Ask user for custom library path
    print_info("Default library path: library/")
    custom_path = input("Enter custom library path (or press Enter for default): ").strip()
    if custom_path:
        config["library_path"] = custom_path
    
    # Ask about debug mode
    debug_response = input("Enable debug mode? (y/N): ").strip().lower()
    config["debug_mode"] = debug_response in ['y', 'yes']
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print_success(f"Configuration saved to {config_path}")
        return True
    except IOError as e:
        print_error(f"Failed to create config file: {e}")
        return False


def create_library_directory():
    """
    Create the library directory.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step("Creating library directory")
    
    project_root = get_project_root()
    config_path = project_root / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        library_path = project_root / config.get("library_path", "library")
        library_path.mkdir(parents=True, exist_ok=True)
        
        print_success(f"Library directory created at {library_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create library directory: {e}")
        return False


def create_cli_wrapper():
    """
    Create a CLI wrapper script to make the tool easily accessible.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print_step("Creating CLI wrapper")
    
    project_root = get_project_root()
    
    if platform.system() == "Windows":
        wrapper_path = project_root / "rb.bat"
        wrapper_content = f"""@echo off
"{get_venv_python()}" -m src.cli %*
"""
    else:
        wrapper_path = project_root / "rb"
        wrapper_content = f"""#!/bin/bash
"{get_venv_python()}" -m src.cli "$@"
"""
    
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(wrapper_path, 0o755)
        
        print_success(f"CLI wrapper created at {wrapper_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create CLI wrapper: {e}")
        return False


def verify_installation():
    """
    Verify that the installation was successful.
    
    Returns:
        bool: True if verification passed, False otherwise
    """
    print_step("Verifying installation")
    
    python_path = get_venv_python()
    
    try:
        # Try to import the main module
        result = subprocess.run(
            [str(python_path), '-c', 'import src.cli; print("OK")'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "OK" in result.stdout:
            print_success("Module imports successful")
        else:
            print_error("Failed to import modules")
            return False
        
        # Check easyeda2kicad
        result = subprocess.run(
            [str(python_path), '-c', 'import subprocess; subprocess.run(["easyeda2kicad", "--version"])'],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("easyeda2kicad is accessible")
        else:
            print_info("easyeda2kicad may not be installed (will be checked at runtime)")
        
        return True
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False


def print_usage_instructions():
    """Print instructions for using the tool."""
    project_root = get_project_root()
    
    if platform.system() == "Windows":
        cli_command = ".\\rb.bat"
    else:
        cli_command = "./rb"
    
    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    print("\nTo use the KiCad Library Manager:")
    print(f"\n1. Navigate to: {project_root}")
    print(f"2. Run: {cli_command} --help")
    print("\nExample commands:")
    print(f"  {cli_command} get C12345           # Download a component")
    print(f"  {cli_command} list                 # List all components")
    print(f"  {cli_command} diagnostics          # Run health checks")
    print(f"  {cli_command} --help               # Show all commands")
    print("\n" + "="*60 + "\n")


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("  KiCad Library Manager - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create configuration
    if not create_config_file():
        return 1
    
    # Create library directory
    if not create_library_directory():
        return 1
    
    # Create CLI wrapper
    if not create_cli_wrapper():
        return 1
    
    # Verify installation
    if not verify_installation():
        print_info("Verification had warnings, but setup completed")
    
    # Print usage instructions
    print_usage_instructions()
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)