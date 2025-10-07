"""
YSA Signal - Standalone Signal Analyzer

Process .brw/.h5 files and save/load processed data.
Supports both CLI and GUI modes.

Developer: Jake Cahoon
"""

from ysa_signal import main
from _version import __version__

__author__ = 'Jake Cahoon'
__email__ = 'jacobbcahoon@gmail.com'

# Check for updates
_update_check_done = False


def _check_for_updates():
    """Check if a newer version is available on PyPI"""
    global _update_check_done
    if _update_check_done:
        return
    _update_check_done = True

    try:
        import urllib.request
        import json
        import sys

        # Fetch latest version from PyPI
        url = "https://pypi.org/pypi/ysa-signal/json"
        with urllib.request.urlopen(url, timeout=1) as response:
            data = json.loads(response.read().decode())
            latest_version = data['info']['version']

            # Compare versions
            if latest_version != __version__:
                print(f"\n\033[93m┌{'─' * 50}┐", file=sys.stderr)
                print(f"│ Update available: {__version__} → {latest_version}".ljust(
                    51) + "│", file=sys.stderr)
                print(
                    "│ Run: pip install -U --force-reinstall ysa-signal".ljust(51) + "│", file=sys.stderr)
                print(f"└{'─' * 50}┘\033[0m\n", file=sys.stderr)
    except Exception:
        # Silently fail if check fails (offline, timeout, etc.)
        pass


# Run update check in background (non-blocking)
try:
    import threading
    threading.Thread(target=_check_for_updates, daemon=True).start()
except Exception:
    pass

# Import main entry point

# Import helper functions for programmatic use
try:
    from helper_functions import (
        process_and_store,
        save_processed_data,
        load_processed_data,
        get_channel_data,
        cpp_available,
    )
except ImportError:
    # C++ extensions not yet built
    cpp_available = False

__all__ = [
    'main',
    'process_and_store',
    'save_processed_data',
    'load_processed_data',
    'get_channel_data',
    'cpp_available',
]
