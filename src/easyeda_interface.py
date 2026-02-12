"""
Interface wrapper for easyEDA2kicad tool.
Handles all interactions with the easyEDA2kicad command-line tool.
"""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple


def check_easyeda2kicad_installed() -> bool:
    """
    Check if easyEDA2kicad is installed and accessible.
    
    Returns:
        bool: True if easyEDA2kicad is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['easyeda2kicad', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        logging.debug(f"easyEDA2kicad version check: {result.stdout}")
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.debug(f"easyEDA2kicad not found: {e}")
        return False


def get_easyeda2kicad_version() -> Optional[str]:
    """
    Get the installed version of easyEDA2kicad.
    
    Returns:
        Optional[str]: Version string if available, None otherwise
    """
    try:
        result = subprocess.run(
            ['easyeda2kicad', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse version from output
            version_output = result.stdout.strip()
            logging.debug(f"easyEDA2kicad version output: {version_output}")
            return version_output
        return None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def download_component(component_id: str, output_dir: Path, component_type: str = "symbol") -> Tuple[bool, str]:
    """
    Download a component from EasyEDA using easyEDA2kicad.
    
    Args:
        component_id: EasyEDA component ID (LCSC part number or EasyEDA ID)
        output_dir: Directory where the component files should be saved
        component_type: Type of component to download (symbol, footprint, or both)
        
    Returns:
        Tuple[bool, str]: (Success status, message describing the result)
    """
    if not check_easyeda2kicad_installed():
        return False, "easyEDA2kicad is not installed or not accessible"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logging.debug(f"Downloading component {component_id} to {output_dir}")
        
        # Build the easyEDA2kicad command
        # Note: Actual command structure may need adjustment based on easyEDA2kicad's API
        cmd = [
            'easyeda2kicad',
            '--lcsc_id', component_id,
            '--output', str(output_dir),
            '--overwrite'
        ]
        
        # Add component type flag if needed
        if component_type == "symbol":
            cmd.append('--symbol')
        elif component_type == "footprint":
            cmd.append('--footprint')
        elif component_type == "both":
            cmd.extend(['--symbol', '--footprint'])
        
        logging.debug(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # Allow up to 60 seconds for download
        )
        
        if result.returncode == 0:
            logging.debug(f"Component download successful: {result.stdout}")
            return True, f"Successfully downloaded component {component_id}"
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            logging.error(f"Component download failed: {error_msg}")
            return False, f"Failed to download component: {error_msg}"
            
    except subprocess.TimeoutExpired:
        error_msg = "Download timed out after 60 seconds"
        logging.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error during download: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def validate_component_id(component_id: str) -> bool:
    """
    Validate that a component ID is in a reasonable format.
    
    Args:
        component_id: Component identifier to validate
        
    Returns:
        bool: True if the ID appears valid, False otherwise
    """
    if not component_id:
        return False
    
    # Basic validation - component IDs are typically alphanumeric
    # LCSC part numbers typically start with 'C' followed by numbers
    component_id = component_id.strip()
    
    if len(component_id) < 2:
        return False
    
    # Allow alphanumeric characters, hyphens, and underscores
    if not all(c.isalnum() or c in ['-', '_'] for c in component_id):
        logging.error(f"Component ID contains invalid characters: {component_id}")
        return False
    
    return True


def search_component(search_term: str) -> Tuple[bool, str]:
    """
    Search for components in EasyEDA library.
    
    Args:
        search_term: Search query string
        
    Returns:
        Tuple[bool, str]: (Success status, search results or error message)
    """
    if not check_easyeda2kicad_installed():
        return False, "easyEDA2kicad is not installed or not accessible"
    
    try:
        logging.debug(f"Searching for component: {search_term}")
        
        # Note: This is a placeholder - actual search functionality depends on easyEDA2kicad's capabilities
        # Some versions may not support search directly
        cmd = [
            'easyeda2kicad',
            '--search', search_term
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, "Search functionality not available or search failed"
            
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logging.debug(f"Search failed: {e}")
        return False, "Search functionality not available"