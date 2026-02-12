#!/usr/bin/env python3
"""
KiCad Library Manager - Command Line Interface
Main entry point for the CLI tool.
"""

import argparse
import sys
import logging

from . import utils
from . import component_manager
from . import diagnostics


def cmd_get(args) -> int:
    """
    Handle the 'get' command to download a component.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    component_id = args.component_id
    component_type = args.type
    
    success, message = component_manager.get_component(component_id, component_type)
    
    if success:
        print(utils.format_success(message))
        return 0
    else:
        print(utils.format_error(message))
        return 1


def cmd_delete(args) -> int:
    """
    Handle the 'delete' command to remove a component.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    component_id = args.component_id
    
    # Ask for confirmation unless --force is used
    if not args.force:
        response = input(f"Are you sure you want to delete component '{component_id}'? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Delete cancelled.")
            return 0
    
    success, message = component_manager.delete_component(component_id)
    
    if success:
        print(utils.format_success(message))
        return 0
    else:
        print(utils.format_error(message))
        return 1


def cmd_list(args) -> int:
    """
    Handle the 'list' command to show all components.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    verbose = args.verbose
    components = component_manager.list_components(verbose=verbose)
    
    if not components:
        print(utils.format_info("No components found in library"))
        return 0
    
    print(f"\nFound {len(components)} component(s) in library:\n")
    
    for component in components:
        component_id = component['id']
        file_count = component.get('file_count', 0)
        
        if verbose:
            # Show detailed information
            print(f"📦 {component_id}")
            print(f"   Files: {file_count}")
            
            if 'component_type' in component:
                print(f"   Type: {component['component_type']}")
            
            if 'added_date' in component:
                print(f"   Added: {component['added_date']}")
            
            if 'files' in component and component['files']:
                print(f"   Contents: {', '.join(component['files'][:3])}")
                if len(component['files']) > 3:
                    print(f"             ... and {len(component['files']) - 3} more")
            
            print()
        else:
            # Simple listing
            print(f"  • {component_id} ({file_count} files)")
    
    if not verbose:
        print(f"\nUse 'list --verbose' for more details")
    
    return 0


def cmd_info(args) -> int:
    """
    Handle the 'info' command to show details about a specific component.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    component_id = args.component_id
    info = component_manager.get_component_info(component_id)
    
    if not info:
        print(utils.format_error(f"Component '{component_id}' not found in library"))
        return 1
    
    print(f"\n📦 Component: {component_id}\n")
    print(f"Path: {info['path']}")
    print(f"Files: {info['file_count']}")
    
    if 'component_type' in info:
        print(f"Type: {info['component_type']}")
    
    if 'added_date' in info:
        print(f"Added: {info['added_date']}")
    
    if 'files' in info and info['files']:
        print(f"\nContents:")
        for filename in info['files']:
            print(f"  • {filename}")
    
    print()
    return 0


def cmd_diagnostics(args) -> int:
    """
    Handle the 'diagnostics' command to run system checks.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 if all checks pass, 1 if any fail)
    """
    checks = diagnostics.run_diagnostics(verbose=args.verbose)
    diagnostics.print_diagnostic_report(checks)
    
    # Return non-zero if any critical checks failed
    all_passed = all(check.passed for check in checks)
    return 0 if all_passed else 1


def cmd_rebuild(args) -> int:
    """
    Handle the 'rebuild' command to regenerate master library files.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Rebuilding master library files...")
    
    success, message = component_manager.rebuild_master_libraries()
    
    if success:
        print(utils.format_success(message))
        print("\nMaster library files created:")
        library_path = utils.get_library_path()
        print(f"  Symbols:    {library_path}/kicad-library-manager.kicad_sym")
        print(f"  Footprints: {library_path}/kicad-library-manager.pretty/")
        return 0
    else:
        print(utils.format_error(message))
        return 1


def main():
    """
    Main entry point for the CLI.
    """
    # Create main parser
    parser = argparse.ArgumentParser(
        prog='kicad-lib',
        description='KiCad Library Manager - Manage EasyEDA components for KiCad',
        epilog='Use "kicad-lib <command> --help" for more information about a command.'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='KiCad Library Manager v1.0.0'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        help='Available commands'
    )
    
    # Get command
    parser_get = subparsers.add_parser(
        'get',
        help='Download and add a component to the library'
    )
    parser_get.add_argument(
        'component_id',
        help='EasyEDA component ID or LCSC part number (e.g., C12345)'
    )
    parser_get.add_argument(
        '--type',
        choices=['symbol', 'footprint', 'both'],
        default='both',
        help='Type of component to download (default: both)'
    )
    parser_get.set_defaults(func=cmd_get)
    
    # Delete command
    parser_delete = subparsers.add_parser(
        'delete',
        help='Remove a component from the library'
    )
    parser_delete.add_argument(
        'component_id',
        help='Component ID to remove'
    )
    parser_delete.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser_delete.set_defaults(func=cmd_delete)
    
    # List command
    parser_list = subparsers.add_parser(
        'list',
        help='List all components in the library'
    )
    parser_list.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information about each component'
    )
    parser_list.set_defaults(func=cmd_list)
    
    # Info command
    parser_info = subparsers.add_parser(
        'info',
        help='Show detailed information about a specific component'
    )
    parser_info.add_argument(
        'component_id',
        help='Component ID to query'
    )
    parser_info.set_defaults(func=cmd_info)
    
    # Diagnostics command
    parser_diag = subparsers.add_parser(
        'diagnostics',
        help='Run system health checks'
    )
    parser_diag.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show additional diagnostic information'
    )
    parser_diag.set_defaults(func=cmd_diagnostics)
    
    # Rebuild command
    parser_rebuild = subparsers.add_parser(
        'rebuild',
        help='Rebuild master library files from all components'
    )
    parser_rebuild.set_defaults(func=cmd_rebuild)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Load configuration and setup logging
    config = utils.load_config()
    debug_mode = args.debug or config.get('debug_mode', False)
    utils.setup_logging(debug_mode)
    
    # Execute the appropriate command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=debug_mode)
        print(utils.format_error(f"An error occurred: {str(e)}"))
        return 1


if __name__ == '__main__':
    sys.exit(main())