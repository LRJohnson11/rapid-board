"""
Component management module.
Handles operations for getting, deleting, and listing components in the library.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import json

from . import utils
from . import easyeda_interface


def get_component(component_id: str, component_type: str = "both") -> Tuple[bool, str]:
    """
    Download and add a component to the library.
    
    Args:
        component_id: EasyEDA component identifier (LCSC part number or EasyEDA ID)
        component_type: Type of component to download ('symbol', 'footprint', or 'both')
        
    Returns:
        Tuple[bool, str]: (Success status, descriptive message)
    """
    logging.info(f"Getting component: {component_id}")
    
    # Validate component ID
    if not easyeda_interface.validate_component_id(component_id):
        return False, f"Invalid component ID: {component_id}"
    
    # Get library path
    library_path = utils.get_library_path()
    
    # Ensure library directory exists
    if not utils.ensure_directory_exists(library_path):
        return False, "Failed to access library directory"
    
    # Create component-specific directory
    component_dir = library_path / component_id
    
    # Check if component already exists
    if component_dir.exists():
        logging.warning(f"Component {component_id} already exists in library")
        return False, f"Component {component_id} already exists. Use delete first to replace."
    
    # Download the component
    success, message = easyeda_interface.download_component(
        component_id, 
        component_dir,
        component_type
    )
    
    if success:
        # Create metadata file for the component
        metadata = {
            "component_id": component_id,
            "component_type": component_type,
            "added_date": utils.get_current_timestamp()
        }
        
        metadata_path = component_dir / "metadata.json"
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logging.debug(f"Created metadata file: {metadata_path}")
        except Exception as e:
            logging.warning(f"Failed to create metadata: {e}")
        
        logging.info(f"Successfully added component {component_id}")
        return True, f"Component {component_id} added to library"
    else:
        # Clean up failed download directory if it was created
        if component_dir.exists():
            try:
                shutil.rmtree(component_dir)
                logging.debug(f"Cleaned up failed download directory: {component_dir}")
            except Exception as e:
                logging.warning(f"Failed to clean up directory: {e}")
        
        return False, message


def delete_component(component_id: str) -> Tuple[bool, str]:
    """
    Remove a component from the library.
    
    Args:
        component_id: Component identifier to remove
        
    Returns:
        Tuple[bool, str]: (Success status, descriptive message)
    """
    logging.info(f"Deleting component: {component_id}")
    
    # Validate component name
    if not utils.validate_component_name(component_id):
        return False, f"Invalid component ID: {component_id}"
    
    # Get library path
    library_path = utils.get_library_path()
    component_dir = library_path / component_id
    
    # Check if component exists
    if not component_dir.exists():
        logging.warning(f"Component {component_id} not found in library")
        return False, f"Component {component_id} not found in library"
    
    # Delete the component directory
    try:
        shutil.rmtree(component_dir)
        logging.info(f"Successfully deleted component {component_id}")
        return True, f"Component {component_id} removed from library"
    except Exception as e:
        error_msg = f"Failed to delete component {component_id}: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def list_components(verbose: bool = False) -> List[dict]:
    """
    List all components in the library.
    
    Args:
        verbose: If True, include detailed information about each component
        
    Returns:
        List[dict]: List of component information dictionaries
    """
    logging.info("Listing components in library")
    
    library_path = utils.get_library_path()
    
    # Check if library exists
    if not library_path.exists():
        logging.warning("Library directory does not exist")
        return []
    
    components = []
    
    # Iterate through library directory
    for item in library_path.iterdir():
        if item.is_dir():
            component_info = {
                "id": item.name,
                "path": str(item)
            }
            
            # Try to load metadata if it exists
            metadata_path = item / "metadata.json"
            if metadata_path.exists() and verbose:
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        component_info.update(metadata)
                except Exception as e:
                    logging.debug(f"Failed to load metadata for {item.name}: {e}")
            
            # Count files in component directory
            file_count = len([f for f in item.iterdir() if f.is_file()])
            component_info["file_count"] = file_count
            
            components.append(component_info)
            logging.debug(f"Found component: {item.name}")
    
    logging.info(f"Found {len(components)} components in library")
    return components


def get_component_info(component_id: str) -> Optional[dict]:
    """
    Get detailed information about a specific component.
    
    Args:
        component_id: Component identifier to query
        
    Returns:
        Optional[dict]: Component information dictionary, or None if not found
    """
    library_path = utils.get_library_path()
    component_dir = library_path / component_id
    
    if not component_dir.exists():
        return None
    
    component_info = {
        "id": component_id,
        "path": str(component_dir)
    }
    
    # Load metadata
    metadata_path = component_dir / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                component_info.update(metadata)
        except Exception as e:
            logging.debug(f"Failed to load metadata: {e}")
    
    # List files
    files = [f.name for f in component_dir.iterdir() if f.is_file()]
    component_info["files"] = files
    component_info["file_count"] = len(files)
    
    return component_info


def component_exists(component_id: str) -> bool:
    """
    Check if a component exists in the library.
    
    Args:
        component_id: Component identifier to check
        
    Returns:
        bool: True if component exists, False otherwise
    """
    library_path = utils.get_library_path()
    component_dir = library_path / component_id
    return component_dir.exists() and component_dir.is_dir()