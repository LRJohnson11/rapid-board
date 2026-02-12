"""
Component management module.
Handles operations for getting, deleting, and listing components in the library.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import json
import re

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
        
        # Rebuild master libraries
        rebuild_master_libraries()
        
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
        
        # Rebuild master libraries
        rebuild_master_libraries()
        
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


def rebuild_master_libraries() -> Tuple[bool, str]:
    """
    Rebuild the master symbol and footprint library files from all components.
    Creates consolidated library files that KiCad can easily import.
    
    Returns:
        Tuple[bool, str]: (Success status, descriptive message)
    """
    logging.info("Rebuilding master library files...")
    
    library_path = utils.get_library_path()
    
    # Ensure library directory exists
    if not library_path.exists():
        return False, "Library directory does not exist"
    
    try:
        # Rebuild symbol library
        symbol_success, symbol_msg = _rebuild_symbol_library(library_path)
        
        # Rebuild footprint library
        footprint_success, footprint_msg = _rebuild_footprint_library(library_path)
        
        if symbol_success and footprint_success:
            logging.info("Master libraries rebuilt successfully")
            return True, "Master libraries updated"
        else:
            messages = []
            if not symbol_success:
                messages.append(f"Symbol library: {symbol_msg}")
            if not footprint_success:
                messages.append(f"Footprint library: {footprint_msg}")
            return False, "; ".join(messages)
            
    except Exception as e:
        error_msg = f"Failed to rebuild master libraries: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def _rebuild_symbol_library(library_path: Path) -> Tuple[bool, str]:
    """
    Rebuild the master symbol library file from all component symbols.
    
    Args:
        library_path: Path to the library directory
        
    Returns:
        Tuple[bool, str]: (Success status, message)
    """
    master_symbol_file = library_path / "kicad-library-manager.kicad_sym"
    
    # Start with KiCad symbol library header
    library_content = ['(kicad_symbol_lib (version 20211014) (generator kicad-library-manager)\n']
    
    symbol_count = 0
    
    # Iterate through all component directories
    for component_dir in sorted(library_path.iterdir()): ##FIXME The bug here is its looking at directories, but the kicad.sym is not stored in a library there
        if not component_dir.is_dir():
            continue
            
        # Look for symbol files
        symbol_files = list(component_dir.glob("*.kicad_sym"))
        
        for symbol_file in symbol_files:
            try:
                with open(symbol_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract symbol definitions (skip the header and footer)
                # KiCad symbol files have format: (kicad_symbol_lib ... (symbol ...) ...)
                # We want to extract just the (symbol ...) parts
                symbol_defs = _extract_symbol_definitions(content)
                
                if symbol_defs:
                    library_content.extend(symbol_defs)
                    symbol_count += len(symbol_defs)
                    logging.debug(f"Added {len(symbol_defs)} symbols from {symbol_file.name}")
                    
            except Exception as e:
                logging.warning(f"Failed to process symbol file {symbol_file}: {e}")
                continue
    
    # Close the library
    library_content.append(')\n')
    
    # Write the master symbol library
    try:
        with open(master_symbol_file, 'w', encoding='utf-8') as f:
            f.writelines(library_content)
        
        logging.info(f"Created master symbol library with {symbol_count} symbols")
        return True, f"Symbol library created ({symbol_count} symbols)"
        
    except Exception as e:
        return False, f"Failed to write symbol library: {str(e)}"


def _rebuild_footprint_library(library_path: Path) -> Tuple[bool, str]:
    """
    Rebuild the master footprint library directory from all component footprints.
    KiCad footprint libraries are directories containing .kicad_mod files.
    
    Args:
        library_path: Path to the library directory
        
    Returns:
        Tuple[bool, str]: (Success status, message)
    """
    master_footprint_dir = library_path / "kicad-library-manager.pretty"
    
    # Create/clear the master footprint directory
    if master_footprint_dir.exists():
        # Clear existing footprints but keep the directory
        for item in master_footprint_dir.iterdir():
            if item.is_file() and item.suffix == '.kicad_mod':
                item.unlink()
    else:
        master_footprint_dir.mkdir(exist_ok=True)
    
    footprint_count = 0
    
    # Iterate through all component directories
    for component_dir in sorted(library_path.iterdir()):
        if not component_dir.is_dir() or component_dir.name == "kicad-library-manager.pretty":
            continue
            
        # Look for footprint files
        footprint_files = list(component_dir.glob("*.kicad_mod"))
        
        for footprint_file in footprint_files:
            try:
                # Create a unique footprint name using component ID
                component_id = component_dir.name
                new_footprint_name = f"{component_id}_{footprint_file.stem}.kicad_mod"
                destination = master_footprint_dir / new_footprint_name
                
                # Copy the footprint file
                shutil.copy2(footprint_file, destination)
                footprint_count += 1
                logging.debug(f"Copied footprint: {new_footprint_name}")
                
            except Exception as e:
                logging.warning(f"Failed to copy footprint {footprint_file}: {e}")
                continue
    
    logging.info(f"Created master footprint library with {footprint_count} footprints")
    return True, f"Footprint library created ({footprint_count} footprints)"


def _extract_symbol_definitions(content: str) -> List[str]:
    """
    Extract symbol definitions from a KiCad symbol library file.
    
    Args:
        content: Content of a .kicad_sym file
        
    Returns:
        List[str]: List of symbol definition strings
    """
    symbols = []
    
    # Find all (symbol ...) blocks
    # We need to match balanced parentheses
    depth = 0
    current_symbol = []
    in_symbol = False
    
    i = 0
    while i < len(content):
        # Look for "(symbol " pattern
        if content[i:i+8] == "(symbol ":
            in_symbol = True
            depth = 1
            current_symbol = ["(symbol "]
            i += 8
            continue
        
        if in_symbol:
            current_symbol.append(content[i])
            
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                
                if depth == 0:
                    # Complete symbol found
                    symbol_text = ''.join(current_symbol)
                    symbols.append(symbol_text + '\n')
                    in_symbol = False
                    current_symbol = []
        
        i += 1
    
    return symbols