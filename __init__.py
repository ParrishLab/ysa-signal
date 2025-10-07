"""
YSA Signal - Standalone Signal Analyzer

Process .brw/.h5 files and save/load processed data.
Supports both CLI and GUI modes.

Developer: Jake Cahoon
"""

__version__ = '1.0.3'
__author__ = 'Jake Cahoon'
__email__ = 'jacobbcahoon@gmail.com'

# Import main entry point
from ysa_signal import main

# Import helper functions for programmatic use
try:
    from helper_functions import (
        process_and_store,
        save_processed_data,
        load_processed_data,
        get_channel_data,
        CPP_AVAILABLE,
    )
except ImportError:
    # C++ extensions not yet built
    CPP_AVAILABLE = False

__all__ = [
    'main',
    'process_and_store',
    'save_processed_data',
    'load_processed_data',
    'get_channel_data',
    'CPP_AVAILABLE',
]
