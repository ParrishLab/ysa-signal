# YSA Signal

**Standalone signal analyzer for downsampled .brw files**

YSA Signal processes MEA recordings from downsampled .brw files, detects seizures and status epilepticus events, and saves the results in a compact HDF5 format. Mac only for now.

## Installation

```bash
pip install ysa-signal
```

## Usage

### GUI Mode

To run the GUI, just run this command after installation:
```bash
ysa-signal
```

The GUI provides two tabs:

- **Process Files**: Select input files, optionally enable seizure analysis, and save processed data
- **View Signals**: Load processed files and view signals in an interactive 64x64 channel grid

### CLI Mode

```bash
# Process without analysis (faster)
ysa-signal input.brw output_processed.h5

# Process with seizure analysis
ysa-signal input.brw output_processed.h5 --do-analysis
```

### Python API

```python
from ysa_signal import process_and_store, save_processed_data, load_processed_data

# Read in downsampled .brw file, process it, and store the results in memory (not on disk on a file)
processed_data = process_and_store('/path/to/file.brw', do_analysis=True)

# Save the processed data to an h5 file (on disk on a file you specify)
save_processed_data(processed_data, '/path/to/file_processed.h5')

# With already processed data saved to an h5 file, you can load it back into memory
loaded_data = load_processed_data('/path/to/file_processed.h5')

# Example: Accessing data for a specific channel (row, col)
row = loaded_data.active_channels[0][0]
col = loaded_data.active_channels[0][1]

# Access the signal and seizure times for the specified channel
channel_data = loaded_data.data[row - 1, col - 1]
signal = channel_data['signal']
sz_times = channel_data['SzTimes']
```

### Batch Processing Example

```python
from ysa_signal import process_and_store, save_processed_data
import glob

for brw_file in glob.glob('data/*.brw'):
    output_file = brw_file.replace('.brw', '_processed.h5')
    processed_data = process_and_store(brw_file, do_analysis=True)
    save_processed_data(processed_data, output_file)
```

## Support

- GitHub: [github.com/ParrishLab/ysa-signal](https://github.com/ParrishLab/ysa-signal/issues)
- Email: jacobbcahoon@gmail.com
- Phone: (385) 307-9925
