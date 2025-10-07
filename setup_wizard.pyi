"""Type stubs for setup_wizard module"""

from typing import Optional, List, Tuple

def check_python_version() -> bool:
    """Check if Python version meets requirements (>=3.6)"""
    ...

def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if required Python packages are installed.

    Returns:
        Tuple of (all_installed: bool, missing_packages: List[str])
    """
    ...

def install_dependencies(packages: List[str]) -> bool:
    """
    Install missing Python packages.

    Args:
        packages: List of package names to install

    Returns:
        True if installation successful, False otherwise
    """
    ...

def find_hdf5() -> Optional[str]:
    """
    Try to find HDF5 installation.

    Returns:
        Path to HDF5 installation or None if not found
    """
    ...

def compile_extensions() -> bool:
    """
    Compile C++ extensions.

    Returns:
        True if compilation successful, False otherwise
    """
    ...

def verify_installation() -> bool:
    """
    Verify that extensions compiled successfully.

    Returns:
        True if extensions can be imported, False otherwise
    """
    ...

def main() -> int:
    """
    Main setup wizard entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    ...
