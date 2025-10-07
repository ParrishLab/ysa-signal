"""Type stubs for helper_functions module"""

from typing import Tuple, List, Dict, Any, Optional
import numpy as np

# Flag indicating if C++ extensions are available
CPP_AVAILABLE: bool

class ProcessedData:
    """Container for processed signal data"""

    sampling_rate: float
    num_rec_frames: int
    recording_length: float
    time_vector: np.ndarray
    active_channels: List[Tuple[int, int]]
    data: np.ndarray  # 64x64 array of channel data dictionaries
    original_metadata: Dict[str, Any]

    def __init__(
        self,
        sampling_rate: float,
        num_rec_frames: int,
        recording_length: float,
        time_vector: np.ndarray,
        active_channels: List[Tuple[int, int]],
        data: np.ndarray,
        original_metadata: Dict[str, Any]
    ) -> None: ...

def process_and_store(
    input_file: str,
    do_analysis: bool = False
) -> ProcessedData:
    """
    Process a .brw/.h5 file and return processed data.

    Args:
        input_file: Path to input .brw/.h5 file
        do_analysis: Whether to perform seizure/SE detection analysis

    Returns:
        ProcessedData object containing all processed information

    Raises:
        RuntimeError: If C++ extensions are not available
        FileNotFoundError: If input file doesn't exist
    """
    ...

def save_processed_data(
    processed_data: ProcessedData,
    output_file: str
) -> None:
    """
    Save processed data to HDF5 file.

    Args:
        processed_data: ProcessedData object to save
        output_file: Path to output .h5 file

    Raises:
        IOError: If file cannot be written
    """
    ...

def load_processed_data(input_file: str) -> ProcessedData:
    """
    Load processed data from HDF5 file.

    Args:
        input_file: Path to processed .h5 file

    Returns:
        ProcessedData object containing loaded information

    Raises:
        FileNotFoundError: If input file doesn't exist
        IOError: If file cannot be read
    """
    ...

def get_channel_data(
    processed_data: ProcessedData,
    row: int,
    col: int
) -> Optional[Dict[str, Any]]:
    """
    Get data for a specific channel.

    Args:
        processed_data: ProcessedData object
        row: Channel row (0-63)
        col: Channel column (0-63)

    Returns:
        Dictionary containing:
            - 'signal': np.ndarray of voltage values
            - 'SzTimes': List of [start, end] seizure times
            - 'SETimes': List of [start, end] SE times
            - 'DischargeTimes': List of discharge times
        Returns None if channel has no data
    """
    ...
