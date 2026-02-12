"""
Utility functions for the KiCad Library Manager.
Handles configuration management, logging, and shared helper functions.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def get_project_root() -> Path:
    """
    Get the root directory of the project.
    
    Returns:
        Path: Absolute path to the project root directory
    """
    return Path(__file__).parent.parent.resolve()


def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    
    Returns:
        Path: Absolute path to config.json
    """
    return get_project_root() / "config.json"


def get_library_path() -> Path:
    """
    Get the path to the component library directory.
    
    Returns:
        Path: Absolute path to the library directory
    """
    config = load_config()
    library_relative_path = config.get("library_path", "library")
    return get_project_root() / library_relative_path


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with user settings
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return get_default_config()
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Failed to load config: {e}. Using defaults.")
        return get_default_config()


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to config.json.
    
    Args:
        config: Dictionary containing configuration settings
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        logging.error(f"Failed to save config: {e}")
        return False


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration settings.
    
    Returns:
        Dict[str, Any]: Default configuration dictionary
    """
    return {
        "library_path": "library",
        "debug_mode": False,
        "easyeda2kicad_path": None  # Auto-detected during setup
    }


def setup_logging(debug_mode: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        debug_mode: If True, enable verbose debug logging; if False, show only important messages
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_format = '%(levelname)s: %(message)s'
    
    if debug_mode:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        force=True  # Override any existing configuration
    )


def ensure_directory_exists(directory: Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory to check/create
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Directory ensured: {directory}")
        return True
    except OSError as e:
        logging.error(f"Failed to create directory {directory}: {e}")
        return False


def validate_component_name(component_name: str) -> bool:
    """
    Validate that a component name is safe for filesystem operations.
    
    Args:
        component_name: Name of the component to validate
        
    Returns:
        bool: True if component name is valid, False otherwise
    """
    if not component_name:
        return False
    
    # Check for invalid filesystem characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in component_name for char in invalid_chars):
        logging.error(f"Component name contains invalid characters: {component_name}")
        return False
    
    # Check for path traversal attempts
    if '..' in component_name or component_name.startswith('.'):
        logging.error(f"Component name contains invalid path elements: {component_name}")
        return False
    
    return True


def format_success(message: str) -> str:
    """
    Format a success message for display.
    
    Args:
        message: Success message to format
        
    Returns:
        str: Formatted success message
    """
    return f"✓ {message}"


def format_error(message: str) -> str:
    """
    Format an error message for display.
    
    Args:
        message: Error message to format
        
    Returns:
        str: Formatted error message
    """
    return f"✗ {message}"


def format_info(message: str) -> str:
    """
    Format an informational message for display.
    
    Args:
        message: Info message to format
        
    Returns:
        str: Formatted info message
    """
    return f"ℹ {message}"


def get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        str: Current timestamp as ISO 8601 string
    """
    return datetime.now().isoformat()