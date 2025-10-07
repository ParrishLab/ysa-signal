"""
YSA Signal Helper Functions

This module provides helper functions for processing .brw/.h5 files using
C++ extensions and storing/loading the processed data.
"""

import os
import sys
import numpy as np
import h5py
from typing import Dict, Tuple, Optional, Any

from _version import __version__

# Try to import C++ extensions
CPP_AVAILABLE = False
try:
    # Try direct import (when installed via pip as py_modules)
    from sz_se_detect import processAllChannels
    CPP_AVAILABLE = True
except ImportError:
    try:
        # Fallback to local extensions directory (for development)
        extensions_dir = os.path.join(os.path.dirname(__file__), 'extensions')
        if os.path.isdir(extensions_dir):
            sys.path.insert(0, extensions_dir)
        from sz_se_detect import processAllChannels
        CPP_AVAILABLE = True
    except ImportError:
        CPP_AVAILABLE = False
        print("Warning: C++ extension not available. Please run setup first.")


class ProcessedData:
    """Container for processed signal data and metadata"""

    def __init__(self):
        self.data = np.empty((64, 64), dtype=object)
        self.sampling_rate = None
        self.num_rec_frames = None
        self.recording_length = None
        self.time_vector = None
        self.active_channels = []
        self.original_metadata = {}


def extract_original_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract all metadata from the original .brw/.h5 file.

    Args:
        file_path: Path to the original .brw/.h5 file

    Returns:
        Dictionary containing all original metadata
    """
    metadata = {}

    try:
        with h5py.File(file_path, 'r') as f:
            # Extract recording variables
            if '/3BRecInfo/3BRecVars/NRecFrames' in f:
                metadata['NRecFrames'] = int(
                    f['/3BRecInfo/3BRecVars/NRecFrames'][()])
            if '/3BRecInfo/3BRecVars/SamplingRate' in f:
                metadata['SamplingRate'] = float(
                    f['/3BRecInfo/3BRecVars/SamplingRate'][()])
            if '/3BRecInfo/3BRecVars/SignalInversion' in f:
                metadata['SignalInversion'] = float(
                    f['/3BRecInfo/3BRecVars/SignalInversion'][()])
            if '/3BRecInfo/3BRecVars/MaxVolt' in f:
                metadata['MaxVolt'] = float(
                    f['/3BRecInfo/3BRecVars/MaxVolt'][()])
            if '/3BRecInfo/3BRecVars/MinVolt' in f:
                metadata['MinVolt'] = float(
                    f['/3BRecInfo/3BRecVars/MinVolt'][()])
            if '/3BRecInfo/3BRecVars/BitDepth' in f:
                metadata['BitDepth'] = int(
                    f['/3BRecInfo/3BRecVars/BitDepth'][()])

            # Extract root attributes if they exist
            if 'MinAnalogValue' in f.attrs:
                metadata['MinAnalogValue'] = float(f.attrs['MinAnalogValue'])
            if 'MaxAnalogValue' in f.attrs:
                metadata['MaxAnalogValue'] = float(f.attrs['MaxAnalogValue'])
            if 'MinDigitalValue' in f.attrs:
                metadata['MinDigitalValue'] = float(f.attrs['MinDigitalValue'])
            if 'MaxDigitalValue' in f.attrs:
                metadata['MaxDigitalValue'] = float(f.attrs['MaxDigitalValue'])

    except Exception as e:
        print(f"Warning: Could not extract all metadata: {e}")

    return metadata


def process_and_store(file_path: str, do_analysis: bool = True,
                      temp_data_path: Optional[str] = None) -> ProcessedData:
    """
    Process a .brw/.h5 file and store results in a data structure in memory.

    Args:
        file_path: Path to the downsampled .brw file to process
        do_analysis: Whether to perform seizure/SE detection analysis
        temp_data_path: Temporary directory for processing (optional)

    Returns:
        ProcessedData object containing the processed data and metadata

    Raises:
        RuntimeError: If C++ extension is not available
        FileNotFoundError: If the input file doesn't exist
    """
    if not CPP_AVAILABLE:
        raise RuntimeError(
            "C++ extension not available. Please run the setup wizard first."
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # TODO: Deprecate this as it is no longer needed
    if temp_data_path is None:
        temp_data_path = os.path.join(os.path.dirname(__file__), '.temp')

    os.makedirs(temp_data_path, exist_ok=True)

    try:
        # Process all channels using C++ extension
        print(f"Processing {file_path}...")
        results = processAllChannels(file_path, do_analysis, temp_data_path)

        # Create ProcessedData object
        processed = ProcessedData()

        # Store channel data
        for result in results:
            signal = np.array(result.signal, dtype=np.float32).squeeze()
            SzTimes = np.array([(t[0], t[1], t[2]) for t in result.result.SzTimes]
                               ) if result.result.SzTimes else np.array([])
            SETimes = np.array([(t[0], t[1], t[2]) for t in result.result.SETimes]
                               ) if result.result.SETimes else np.array([])
            DischargeTimes = np.array([(t[0], t[1], t[2]) for t in result.result.DischargeTimes]
                                      ) if result.result.DischargeTimes else np.array([])

            processed.data[result.Row - 1, result.Col - 1] = {
                'signal': signal,
                'SzTimes': SzTimes,
                'SETimes': SETimes,
                'DischargeTimes': DischargeTimes,
            }

            processed.active_channels.append((result.Row, result.Col))

        # Extract metadata from original file
        with h5py.File(file_path, 'r') as f:
            processed.num_rec_frames = int(
                f['/3BRecInfo/3BRecVars/NRecFrames'][()])
            processed.sampling_rate = float(
                f['/3BRecInfo/3BRecVars/SamplingRate'][()])

        # Calculate derived metadata
        processed.recording_length = (
            1 / processed.sampling_rate) * (processed.num_rec_frames - 1)
        processed.time_vector = [
            i / processed.sampling_rate for i in range(processed.num_rec_frames)]

        # Store original metadata
        processed.original_metadata = extract_original_metadata(file_path)

        print(
            f"Processing complete! Processed {len(processed.active_channels)} channels.")

        return processed

    finally:
        # Clean up temp directory
        if os.path.exists(temp_data_path):
            for file in os.listdir(temp_data_path):
                if file.endswith('.txt') or file.endswith('.mat'):
                    os.remove(os.path.join(temp_data_path, file))
            try:
                os.rmdir(temp_data_path)
            except OSError:
                pass  # Directory not empty, that's okay


def save_processed_data(processed_data: ProcessedData, output_path: str) -> None:
    """
    Save processed data to a custom HDF5 file format.

    Args:
        processed_data: ProcessedData object containing the data to save
        output_path: Path where the HDF5 file should be saved
    """
    print(f"Saving processed data to {output_path}...")

    with h5py.File(output_path, 'w') as f:
        # Create metadata group
        meta_group = f.create_group('metadata')
        meta_group.create_dataset(
            'sampling_rate', data=processed_data.sampling_rate)
        meta_group.create_dataset(
            'num_rec_frames', data=processed_data.num_rec_frames)
        meta_group.create_dataset(
            'recording_length', data=processed_data.recording_length)
        meta_group.create_dataset('time_vector', data=np.array(
            processed_data.time_vector, dtype=np.float32))

        # Store original metadata
        orig_meta_group = meta_group.create_group('original')
        for key, value in processed_data.original_metadata.items():
            orig_meta_group.create_dataset(key, data=value)

        # Store active channels
        meta_group.create_dataset(
            'active_channels', data=np.array(processed_data.active_channels))

        # Create channels group
        channels_group = f.create_group('channels')

        # Save each channel's data
        for row, col in processed_data.active_channels:
            cell_data = processed_data.data[row - 1, col - 1]
            if cell_data is None:
                continue

            channel_name = f"c_{row}_{col}"
            channel_group = channels_group.create_group(channel_name)

            # Save signal
            channel_group.create_dataset('signal', data=cell_data['signal'],
                                         compression='gzip', compression_opts=6)

            # Save detection results if they exist
            if len(cell_data['SzTimes']) > 0:
                channel_group.create_dataset(
                    'SzTimes', data=cell_data['SzTimes'])
            if len(cell_data['SETimes']) > 0:
                channel_group.create_dataset(
                    'SETimes', data=cell_data['SETimes'])
            if len(cell_data['DischargeTimes']) > 0:
                channel_group.create_dataset(
                    'DischargeTimes', data=cell_data['DischargeTimes'])

    print(f"Successfully saved processed data to {output_path}")


def load_processed_data(file_path: str) -> ProcessedData:
    """
    Load processed data from a custom HDF5 file.

    Args:
        file_path: Path to the processed .h5 file

    Returns:
        ProcessedData object containing the loaded data and metadata

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Loading processed data from {file_path}...")

    processed = ProcessedData()

    with h5py.File(file_path, 'r') as f:
        # Check if this is a valid processed file
        if 'metadata' not in f or 'channels' not in f:
            raise ValueError(f"Invalid processed file format: {file_path}")

        # Load metadata
        meta_group = f['metadata']
        processed.sampling_rate = float(meta_group['sampling_rate'][()])
        processed.num_rec_frames = int(meta_group['num_rec_frames'][()])
        processed.recording_length = float(meta_group['recording_length'][()])
        processed.time_vector = list(meta_group['time_vector'][()])
        processed.active_channels = [
            tuple(ch) for ch in meta_group['active_channels'][()]]

        # Load original metadata
        if 'original' in meta_group:
            orig_meta_group = meta_group['original']
            for key in orig_meta_group.keys():
                processed.original_metadata[key] = orig_meta_group[key][()]

        # Load channel data
        channels_group = f['channels']
        for row, col in processed.active_channels:
            channel_name = f"c_{row}_{col}"
            if channel_name not in channels_group:
                continue

            channel_group = channels_group[channel_name]

            # Load signal
            signal = np.array(channel_group['signal'][:], dtype=np.float32)

            # Load detection results
            SzTimes = np.array(
                channel_group['SzTimes'][:]) if 'SzTimes' in channel_group else np.array([])
            SETimes = np.array(
                channel_group['SETimes'][:]) if 'SETimes' in channel_group else np.array([])
            DischargeTimes = np.array(
                channel_group['DischargeTimes'][:]) if 'DischargeTimes' in channel_group else np.array([])

            processed.data[row - 1, col - 1] = {
                'signal': signal,
                'SzTimes': SzTimes,
                'SETimes': SETimes,
                'DischargeTimes': DischargeTimes,
            }

    print(
        f"Successfully loaded {len(processed.active_channels)} channels from {file_path}")

    return processed


def get_channel_data(processed_data: ProcessedData, row: int, col: int) -> Optional[Dict]:
    """
    Get data for a specific channel.

    Args:
        processed_data: ProcessedData object
        row: Channel row (1-64)
        col: Channel column (1-64)

    Returns:
        Dictionary containing channel data, or None if channel is inactive
    """
    if row < 1 or row > 64 or col < 1 or col > 64:
        raise ValueError(
            f"Invalid channel coordinates: ({row}, {col}). Must be 1-64.")

    return processed_data.data[row - 1, col - 1]


if __name__ == "__main__":
    # Simple test
    if CPP_AVAILABLE:
        print("C++ extension loaded successfully!")
        print("Helper functions are ready to use.")
    else:
        print("C++ extension not available. Please run the setup wizard.")
