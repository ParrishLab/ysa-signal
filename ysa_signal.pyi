"""Type stubs for ysa_signal module"""

from typing import Optional, Literal
import sys

def main() -> int:
    """
    Main entry point for YSA Signal application.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    ...

def cli_mode(input_file: str, output_file: str, do_analysis: bool = False) -> int:
    """
    Run in CLI mode.

    Args:
        input_file: Input file path (.brw/.h5)
        output_file: Output file path (.h5)
        do_analysis: Whether to perform seizure/SE analysis

    Returns:
        Exit code (0 for success, 1 for error)
    """
    ...

def gui_mode() -> int:
    """
    Run in GUI mode with tkinter.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    ...
