"""
Diagnostics module for system health checks.
Performs validation of setup, dependencies, and configuration.
"""

import logging
import sys
from pathlib import Path
from typing import List, Tuple
from . import utils
from . import easyeda_interface


class DiagnosticCheck:
    """
    Represents a single diagnostic check with its result.
    """
    def __init__(self, name: str, passed: bool, message: str):
        """
        Initialize a diagnostic check result.
        
        Args:
            name: Name of the diagnostic check
            passed: Whether the check passed
            message: Detailed message about the check result
        """
        self.name = name
        self.passed = passed
        self.message = message
    
    def __str__(self) -> str:
        """
        Format the diagnostic check for display.
        
        Returns:
            str: Formatted check result
        """
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.name}\n  {self.message}"


def check_python_version() -> DiagnosticCheck:
    """
    Check if Python version meets minimum requirements.
    
    Returns:
        DiagnosticCheck: Result of the Python version check
    """
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    passed = current_version >= min_version
    message = f"Python {current_version[0]}.{current_version[1]} detected"
    
    if not passed:
        message += f" (minimum required: {min_version[0]}.{min_version[1]})"
    
    return DiagnosticCheck("Python Version", passed, message)


def check_config_file() -> DiagnosticCheck:
    """
    Check if configuration file exists and is valid.
    
    Returns:
        DiagnosticCheck: Result of the config file check
    """
    config_path = utils.get_config_path()
    
    if not config_path.exists():
        return DiagnosticCheck(
            "Configuration File",
            False,
            f"config.json not found at {config_path}. Run setup first."
        )
    
    try:
        config = utils.load_config()
        required_keys = ["library_path", "debug_mode"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            return DiagnosticCheck(
                "Configuration File",
                False,
                f"Missing required keys: {', '.join(missing_keys)}"
            )
        
        return DiagnosticCheck(
            "Configuration File",
            True,
            f"Valid configuration found at {config_path}"
        )
    except Exception as e:
        return DiagnosticCheck(
            "Configuration File",
            False,
            f"Failed to load config: {str(e)}"
        )


def check_library_directory() -> DiagnosticCheck:
    """
    Check if library directory exists and is accessible.
    
    Returns:
        DiagnosticCheck: Result of the library directory check
    """
    try:
        library_path = utils.get_library_path()
        
        if not library_path.exists():
            # Try to create it
            if utils.ensure_directory_exists(library_path):
                return DiagnosticCheck(
                    "Library Directory",
                    True,
                    f"Created library directory at {library_path}"
                )
            else:
                return DiagnosticCheck(
                    "Library Directory",
                    False,
                    f"Could not create library directory at {library_path}"
                )
        
        # Check if writable
        test_file = library_path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
            
            # Count components
            component_count = len([d for d in library_path.iterdir() if d.is_dir()])
            
            return DiagnosticCheck(
                "Library Directory",
                True,
                f"Library accessible at {library_path} ({component_count} components)"
            )
        except Exception as e:
            return DiagnosticCheck(
                "Library Directory",
                False,
                f"Library directory not writable: {str(e)}"
            )
            
    except Exception as e:
        return DiagnosticCheck(
            "Library Directory",
            False,
            f"Failed to check library directory: {str(e)}"
        )


def check_easyeda2kicad() -> DiagnosticCheck:
    """
    Check if easyEDA2kicad is installed and accessible.
    
    Returns:
        DiagnosticCheck: Result of the easyEDA2kicad check
    """
    if not easyeda_interface.check_easyeda2kicad_installed():
        return DiagnosticCheck(
            "easyEDA2kicad",
            False,
            "easyEDA2kicad not found. Ensure it's installed in your virtual environment."
        )
    
    version = easyeda_interface.get_easyeda2kicad_version()
    message = "easyEDA2kicad is installed"
    if version:
        message += f" ({version})"
    
    return DiagnosticCheck(
        "easyEDA2kicad",
        True,
        message
    )


def check_virtual_environment() -> DiagnosticCheck:
    """
    Check if running inside a virtual environment.
    
    Returns:
        DiagnosticCheck: Result of the virtual environment check
    """
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        venv_path = sys.prefix
        return DiagnosticCheck(
            "Virtual Environment",
            True,
            f"Running in virtual environment: {venv_path}"
        )
    else:
        return DiagnosticCheck(
            "Virtual Environment",
            False,
            "Not running in a virtual environment (recommended for isolation)"
        )


def check_disk_space() -> DiagnosticCheck:
    """
    Check if sufficient disk space is available.
    
    Returns:
        DiagnosticCheck: Result of the disk space check
    """
    try:
        import shutil
        
        library_path = utils.get_library_path()
        usage = shutil.disk_usage(library_path.parent)
        
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        
        # Warn if less than 1GB free
        sufficient = free_gb >= 1.0
        
        message = f"{free_gb:.2f} GB free of {total_gb:.2f} GB total"
        
        if not sufficient:
            message += " (Warning: Low disk space)"
        
        return DiagnosticCheck(
            "Disk Space",
            sufficient,
            message
        )
    except Exception as e:
        return DiagnosticCheck(
            "Disk Space",
            True,  # Don't fail on this check
            f"Could not check disk space: {str(e)}"
        )


def run_diagnostics(verbose: bool = False) -> List[DiagnosticCheck]:
    """
    Run all diagnostic checks.
    
    Args:
        verbose: If True, include additional diagnostic information
        
    Returns:
        List[DiagnosticCheck]: List of all diagnostic check results
    """
    logging.info("Running system diagnostics...")
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_config_file(),
        check_library_directory(),
        check_easyeda2kicad(),
        check_disk_space()
    ]
    
    return checks


def print_diagnostic_report(checks: List[DiagnosticCheck]) -> None:
    """
    Print a formatted diagnostic report.
    
    Args:
        checks: List of diagnostic check results to display
    """
    print("\n" + "="*60)
    print("KiCad Library Manager - Diagnostic Report")
    print("="*60 + "\n")
    
    passed_count = sum(1 for check in checks if check.passed)
    total_count = len(checks)
    
    for check in checks:
        print(check)
        print()
    
    print("="*60)
    print(f"Results: {passed_count}/{total_count} checks passed")
    print("="*60 + "\n")
    
    if passed_count < total_count:
        print("⚠ Some checks failed. Please review the issues above.")
    else:
        print("✓ All checks passed! System is ready to use.")