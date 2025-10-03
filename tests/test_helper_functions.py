#!/usr/bin/env python3
"""
Unit tests for helper_functions.py
"""

import os
import sys
import unittest
import tempfile
import numpy as np
import h5py
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper_functions import (
    ProcessedData,
    extract_original_metadata,
    save_processed_data,
    load_processed_data,
    get_channel_data,
)


class TestProcessedData(unittest.TestCase):
    """Test ProcessedData class"""

    def test_initialization(self):
        """Test ProcessedData initialization"""
        pd = ProcessedData()

        # Check data array shape and type
        self.assertEqual(pd.data.shape, (64, 64))
        self.assertEqual(pd.data.dtype, object)

        # Check default values
        self.assertIsNone(pd.sampling_rate)
        self.assertIsNone(pd.num_rec_frames)
        self.assertIsNone(pd.recording_length)
        self.assertIsNone(pd.time_vector)
        self.assertEqual(pd.active_channels, [])
        self.assertEqual(pd.original_metadata, {})


class TestExtractOriginalMetadata(unittest.TestCase):
    """Test extract_original_metadata function"""

    def setUp(self):
        """Create a temporary test file"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.h5")

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    def test_extract_with_complete_metadata(self):
        """Test extracting metadata from a file with all fields"""
        # Create test file with metadata
        with h5py.File(self.test_file, 'w') as f:
            rec_vars = f.create_group('/3BRecInfo/3BRecVars')
            rec_vars.create_dataset('NRecFrames', data=1000)
            rec_vars.create_dataset('SamplingRate', data=20000.0)
            rec_vars.create_dataset('SignalInversion', data=1.0)
            rec_vars.create_dataset('MaxVolt', data=3400.0)
            rec_vars.create_dataset('MinVolt', data=-3400.0)
            rec_vars.create_dataset('BitDepth', data=4096)

            f.attrs['MinAnalogValue'] = -3400.0
            f.attrs['MaxAnalogValue'] = 3400.0
            f.attrs['MinDigitalValue'] = 0.0
            f.attrs['MaxDigitalValue'] = 4095.0

        metadata = extract_original_metadata(self.test_file)

        # Verify all fields were extracted
        self.assertEqual(metadata['NRecFrames'], 1000)
        self.assertEqual(metadata['SamplingRate'], 20000.0)
        self.assertEqual(metadata['SignalInversion'], 1.0)
        self.assertEqual(metadata['MaxVolt'], 3400.0)
        self.assertEqual(metadata['MinVolt'], -3400.0)
        self.assertEqual(metadata['BitDepth'], 4096)
        self.assertEqual(metadata['MinAnalogValue'], -3400.0)
        self.assertEqual(metadata['MaxAnalogValue'], 3400.0)
        self.assertEqual(metadata['MinDigitalValue'], 0.0)
        self.assertEqual(metadata['MaxDigitalValue'], 4095.0)

    def test_extract_with_partial_metadata(self):
        """Test extracting metadata from a file with only some fields"""
        with h5py.File(self.test_file, 'w') as f:
            rec_vars = f.create_group('/3BRecInfo/3BRecVars')
            rec_vars.create_dataset('NRecFrames', data=500)
            rec_vars.create_dataset('SamplingRate', data=10000.0)

        metadata = extract_original_metadata(self.test_file)

        # Verify extracted fields
        self.assertEqual(metadata['NRecFrames'], 500)
        self.assertEqual(metadata['SamplingRate'], 10000.0)

        # Verify missing fields are not in dict
        self.assertNotIn('SignalInversion', metadata)
        self.assertNotIn('MaxVolt', metadata)

    def test_extract_from_nonexistent_file(self):
        """Test extracting metadata from a non-existent file"""
        metadata = extract_original_metadata("nonexistent.h5")

        # Should return empty dict without crashing
        self.assertEqual(metadata, {})


class TestSaveLoadProcessedData(unittest.TestCase):
    """Test save_processed_data and load_processed_data functions"""

    def setUp(self):
        """Create test data and temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_output.h5")

        # Create test ProcessedData
        self.test_data = ProcessedData()
        self.test_data.sampling_rate = 20000.0
        self.test_data.num_rec_frames = 1000
        self.test_data.recording_length = 0.05  # 50ms
        self.test_data.time_vector = [i / 20000.0 for i in range(1000)]
        self.test_data.active_channels = [(1, 1), (2, 3), (32, 32)]

        # Add channel data
        for row, col in self.test_data.active_channels:
            signal = np.random.randn(1000).astype(np.float32)
            self.test_data.data[row - 1, col - 1] = {
                'signal': signal,
                'SzTimes': np.array([[0.01, 0.02, 1.0]]),
                'SETimes': np.array([]),
                'DischargeTimes': np.array([]),
            }

        # Add metadata
        self.test_data.original_metadata = {
            'SamplingRate': 20000.0,
            'NRecFrames': 1000,
        }

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        os.rmdir(self.temp_dir)

    def test_save_and_load_roundtrip(self):
        """Test that save and load preserve data correctly"""
        # Save data
        save_processed_data(self.test_data, self.output_file)

        # Verify file was created
        self.assertTrue(os.path.exists(self.output_file))

        # Load data back
        loaded_data = load_processed_data(self.output_file)

        # Verify metadata
        self.assertEqual(loaded_data.sampling_rate, self.test_data.sampling_rate)
        self.assertEqual(loaded_data.num_rec_frames, self.test_data.num_rec_frames)
        self.assertAlmostEqual(loaded_data.recording_length, self.test_data.recording_length, places=5)
        self.assertEqual(len(loaded_data.time_vector), len(self.test_data.time_vector))
        self.assertEqual(set(loaded_data.active_channels), set(self.test_data.active_channels))

        # Verify channel data
        for row, col in self.test_data.active_channels:
            original = self.test_data.data[row - 1, col - 1]
            loaded = loaded_data.data[row - 1, col - 1]

            self.assertIsNotNone(loaded)
            np.testing.assert_array_almost_equal(loaded['signal'], original['signal'], decimal=5)
            np.testing.assert_array_equal(loaded['SzTimes'], original['SzTimes'])
            np.testing.assert_array_equal(loaded['SETimes'], original['SETimes'])
            np.testing.assert_array_equal(loaded['DischargeTimes'], original['DischargeTimes'])

        # Verify original metadata
        self.assertEqual(loaded_data.original_metadata['SamplingRate'],
                        self.test_data.original_metadata['SamplingRate'])

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            load_processed_data("nonexistent.h5")

    def test_load_invalid_format(self):
        """Test loading a file with invalid format raises ValueError"""
        # Create an invalid file
        with h5py.File(self.output_file, 'w') as f:
            f.create_dataset('dummy', data=[1, 2, 3])

        with self.assertRaises(ValueError):
            load_processed_data(self.output_file)

    def test_save_empty_channels(self):
        """Test saving data with no active channels"""
        empty_data = ProcessedData()
        empty_data.sampling_rate = 20000.0
        empty_data.num_rec_frames = 100
        empty_data.recording_length = 0.005
        empty_data.time_vector = [i / 20000.0 for i in range(100)]
        empty_data.active_channels = []
        empty_data.original_metadata = {}

        # Should not crash
        save_processed_data(empty_data, self.output_file)
        loaded_data = load_processed_data(self.output_file)

        self.assertEqual(len(loaded_data.active_channels), 0)


class TestGetChannelData(unittest.TestCase):
    """Test get_channel_data function"""

    def setUp(self):
        """Create test ProcessedData"""
        self.test_data = ProcessedData()
        self.test_data.active_channels = [(1, 1), (5, 10)]

        # Add data for active channels
        self.test_data.data[0, 0] = {
            'signal': np.array([1, 2, 3]),
            'SzTimes': np.array([]),
            'SETimes': np.array([]),
            'DischargeTimes': np.array([]),
        }

        self.test_data.data[4, 9] = {
            'signal': np.array([4, 5, 6]),
            'SzTimes': np.array([]),
            'SETimes': np.array([]),
            'DischargeTimes': np.array([]),
        }

    def test_get_valid_channel(self):
        """Test getting data for a valid active channel"""
        data = get_channel_data(self.test_data, 1, 1)

        self.assertIsNotNone(data)
        np.testing.assert_array_equal(data['signal'], np.array([1, 2, 3]))

    def test_get_inactive_channel(self):
        """Test getting data for an inactive channel returns None"""
        data = get_channel_data(self.test_data, 2, 2)

        self.assertIsNone(data)

    def test_get_channel_with_invalid_coordinates(self):
        """Test that invalid coordinates raise ValueError"""
        with self.assertRaises(ValueError):
            get_channel_data(self.test_data, 0, 1)

        with self.assertRaises(ValueError):
            get_channel_data(self.test_data, 1, 65)

        with self.assertRaises(ValueError):
            get_channel_data(self.test_data, -1, 5)

        with self.assertRaises(ValueError):
            get_channel_data(self.test_data, 70, 70)

    def test_get_channel_at_boundaries(self):
        """Test getting data at valid boundary coordinates"""
        # Test all four corners
        self.test_data.data[0, 0] = {'signal': np.array([1])}
        self.test_data.data[0, 63] = {'signal': np.array([2])}
        self.test_data.data[63, 0] = {'signal': np.array([3])}
        self.test_data.data[63, 63] = {'signal': np.array([4])}

        # Should not raise errors
        data1 = get_channel_data(self.test_data, 1, 1)
        data2 = get_channel_data(self.test_data, 1, 64)
        data3 = get_channel_data(self.test_data, 64, 1)
        data4 = get_channel_data(self.test_data, 64, 64)

        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)
        self.assertIsNotNone(data3)
        self.assertIsNotNone(data4)


class TestProcessedDataIntegrity(unittest.TestCase):
    """Test data integrity and edge cases"""

    def test_large_channel_count(self):
        """Test handling many active channels"""
        pd = ProcessedData()
        pd.sampling_rate = 20000.0
        pd.num_rec_frames = 100
        pd.recording_length = 0.005
        pd.time_vector = [i / 20000.0 for i in range(100)]

        # Add all 64x64 channels
        for row in range(1, 65):
            for col in range(1, 65):
                pd.active_channels.append((row, col))
                pd.data[row - 1, col - 1] = {
                    'signal': np.random.randn(100).astype(np.float32),
                    'SzTimes': np.array([]),
                    'SETimes': np.array([]),
                    'DischargeTimes': np.array([]),
                }

        self.assertEqual(len(pd.active_channels), 4096)

        # Test save/load with many channels
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "large_test.h5")
            save_processed_data(pd, output_file)
            loaded = load_processed_data(output_file)

            self.assertEqual(len(loaded.active_channels), 4096)

    def test_signal_with_events(self):
        """Test saving/loading signals with seizure and SE events"""
        pd = ProcessedData()
        pd.sampling_rate = 20000.0
        pd.num_rec_frames = 1000
        pd.recording_length = 0.05
        pd.time_vector = [i / 20000.0 for i in range(1000)]
        pd.active_channels = [(1, 1)]
        pd.original_metadata = {}

        # Add channel with multiple events
        pd.data[0, 0] = {
            'signal': np.random.randn(1000).astype(np.float32),
            'SzTimes': np.array([
                [0.001, 0.005, 1.0],
                [0.010, 0.015, 1.0],
            ]),
            'SETimes': np.array([
                [0.020, 0.030, 1.0],
            ]),
            'DischargeTimes': np.array([
                [0.001, 0.002, 1.0],
                [0.003, 0.004, 1.0],
            ]),
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "events_test.h5")
            save_processed_data(pd, output_file)
            loaded = load_processed_data(output_file)

            channel_data = loaded.data[0, 0]
            self.assertEqual(len(channel_data['SzTimes']), 2)
            self.assertEqual(len(channel_data['SETimes']), 1)
            self.assertEqual(len(channel_data['DischargeTimes']), 2)


if __name__ == '__main__':
    unittest.main()
