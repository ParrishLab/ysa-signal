# YSA Signal

### Mac only for now - Windows support coming soon

**Standalone signal analyzer for downsampled .brw files**

YSA Signal is a simple application for processing and analyzing data from the lab's downsampled .brw files. It uses optimized C++ extensions with HDF5 to quickly process MEA recordings, detect seizures and status epilepticus events, and save the processed data in a compact format for later analysis. The data pipeline is as follows:

```
  Local Field Potentials recorded on MEA with BrainWave
        │
        ▼
  .brw (HDF5 format that is specific to BrainWave)
        │
        ▼
  ChannelExtract.py (done in the lab to downsample and reformat)
        │
        ▼
  Downsampled .brw (HDF5 format)
        │
        ▼
  YSA Signal (this application)
        │
        ▼
  Processed .h5 (custom HDF5 format with analysis results and mV signal)
```

## Quick Start

### 0. Installation

Clone the repository and navigate to the directory:

```bash
git clone https://github.com/ParrishLab/ysa-signal.git
cd ysa-signal
```

### 1. Run the Setup Wizard

The first time you use YSA Signal, run the setup wizard to install dependencies and compile the C++ extensions:

```bash
python setup_wizard.py
```

The wizard will:

- Check your Python version (3.6+ required)
- Install required Python packages (numpy, h5py, pybind11)
- Detect or guide you to install HDF5
- Compile the C++ extensions
- Verify the installation

### 2. Run the Application

#### GUI Mode (recommended for most users)

Simply run the application without arguments:

```bash
python ysa_signal.py
```

This launches a graphical interface where you can:

- Select input files (Downsampled .brw)
- Choose whether to perform seizure analysis (default is off for speed)
- Save processed data
- View signals in an interactive plot viewer

#### CLI Mode (For advanced uses and automation)

Process a file from the command line:

```bash
# Process without analysis (default)
python ysa_signal.py input.brw output_processed.h5

# Process with analysis
python ysa_signal.py input.brw output_processed.h5 --do-analysis
```

## Output Format

YSA Signal saves processed data in a custom HDF5 format:

```
output.h5
├── metadata/
│   ├── sampling_rate (in Hz)
│   ├── num_rec_frames
│   ├── recording_length (in seconds)
│   ├── time_vector (in seconds)
│   ├── active_channels (list of (row, col) tuples)
│   └── original/ (original metadata from .brw)
│       ├── NRecFrames
│       ├── SamplingRate
│       ├── SignalInversion
│       ├── MaxVolt
│       ├── MinVolt
│       └── ... (all original metadata)
└── channels/
    ├── c_1_1/ (row 1, col 1)
    │   ├── signal (raw signal in mV)
    │   ├── SzTimes
    │   ├── SETimes
    │   └── DischargeTimes
    ├── c_1_2/
    │   └── ...
    └── ...
```

## Using in Python Scripts

You can also use YSA Signal's helper functions in your own Python scripts:

```python
from helper_functions import process_and_store, save_processed_data, load_processed_data

# Process a file
processed_data = process_and_store('input.brw', do_analysis=True)

# Save the processed data
save_processed_data(processed_data, 'output_processed.h5')

# Later, load the processed data
loaded_data = load_processed_data('output_processed.h5')

# Access channel data
channel_data = loaded_data.data[row-1, col-1]
signal = channel_data['signal']
sz_times = channel_data['SzTimes']
```

## Requirements

- Python 3.6 or higher
- numpy
- h5py
- pybind11
- HDF5 C++ library

The setup wizard will help you install all of these.

## HDF5 Installation

HDF5 is required for reading .brw/.h5 files. The setup wizard will try to detect it automatically, but if it can't find it, you can install it via:

### macOS

```bash
# Via Homebrew (recommended for most users)
brew install hdf5

# Or via Conda (recommended if using older macOS version like 12.0)
conda install -c conda-forge hdf5
```

This can come in handy to view hdf5 files: [https://myhdf5.hdfgroup.org/](https://myhdf5.hdfgroup.org/)

### Manual Installation

1. Download from https://github.com/HDFGroup/hdf5/releases
   - Choose the appropriate version for your OS
   - Download the tarball or zip file
2. Extract and install (you should now see an `hdf5` directory with `bin`, `include`, `lib`, etc.)
3. Set `HDF5_DIR` environment variable to the installation path

```bashbash
export HDF5_DIR=/path/to/hdf5
```

## Troubleshooting

### "C++ extension not available"

- Run the setup wizard: `python setup_wizard.py`
- Make sure HDF5 is installed
- Check that pybind11 is installed: `pip install pybind11`

### "Could not find HDF5 installation"

- Install HDF5 using one of the methods above
- Or set the `HDF5_DIR` environment variable: `export HDF5_DIR=/path/to/hdf5`
- Run the setup wizard again

### Compilation errors

- Make sure you have a C++ compiler installed (gcc/clang on macOS, MSVC on Windows)
- Check that Python development headers are installed
- Try updating pybind11: `pip install --upgrade pybind11`

## License

Copyright © 2025 Jake Cahoon

## Support

For issues and questions, please contact jacobbcahoon@gmail.com or shoot me a text at (385) 307-9925
