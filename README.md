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

## Installation

### Option 1: Install via pip (Recommended)

The easiest way to install YSA Signal is via pip:

```bash
pip install ysa-signal
```

This will automatically install all dependencies including numpy, h5py, pybind11, and matplotlib. The C++ extensions are pre-compiled and included in the package, so **no manual HDF5 installation is required**!

After installation, you can run the application with:

```bash
# Launch GUI
ysa-signal

# Or use CLI mode
ysa-signal input.brw output_processed.h5 --do-analysis
```

### Option 2: Install from source (For development)

Clone the repository and navigate to the directory:

```bash
git clone https://github.com/ParrishLab/ysa-signal.git
cd ysa-signal
```

Run the setup wizard to install dependencies and compile the C++ extensions:

```bash
python setup_wizard.py
```

The wizard will:
- Check your Python version (3.6+ required)
- Install required Python packages (numpy, h5py, pybind11)
- Detect or guide you to install HDF5
- Compile the C++ extensions
- Verify the installation

## Usage

### GUI Mode (Recommended for most users)

Launch the graphical interface:

```bash
ysa-signal
```

Or if installed from source:

```bash
python ysa_signal.py
```

The GUI provides:
- **Process Files tab**: Select input files (Downsampled .brw), choose whether to perform seizure analysis (default is off for speed), and save processed data
- **View Signals tab**: Load processed files and view signals in an interactive 64x64 channel grid with matplotlib plotting

### CLI Mode (For advanced uses and automation)

Process a file from the command line:

```bash
# Process without analysis (default)
ysa-signal input.brw output_processed.h5

# Process with analysis
ysa-signal input.brw output_processed.h5 --do-analysis
```

Or if installed from source:

```bash
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

You can also use YSA Signal's functions programmatically in your own Python scripts:

```python
from helper_functions import process_and_store, save_processed_data, load_processed_data, get_channel_data

# Process a file
processed_data = process_and_store('input.brw', do_analysis=True)

# Save the processed data
save_processed_data(processed_data, 'output_processed.h5')

# Later, load the processed data
loaded_data = load_processed_data('output_processed.h5')

# Access channel data
channel_data = get_channel_data(loaded_data, row=0, col=0)
signal = channel_data['signal']
sz_times = channel_data['SzTimes']
se_times = channel_data['SETimes']
```

### Example: Batch Processing

```python
from helper_functions import process_and_store, save_processed_data
import glob

# Process all .brw files in a directory
for brw_file in glob.glob('data/*.brw'):
    output_file = brw_file.replace('.brw', '_processed.h5')
    print(f"Processing {brw_file}...")

    processed_data = process_and_store(brw_file, do_analysis=True)
    save_processed_data(processed_data, output_file)

    print(f"Saved to {output_file}")
```

## Requirements

- Python 3.6 or higher
- macOS 10.0 or higher (tested on macOS 10.15+)
- numpy
- h5py
- pybind11
- matplotlib

When installing via pip, all dependencies are automatically installed. The package uses h5py's bundled HDF5 library, so **no separate HDF5 installation is required**.

## Testing

YSA Signal includes comprehensive unit tests to ensure reliability. To run the tests:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=term

# Run specific test file
pytest tests/test_helper_functions.py -v
```

### Continuous Integration

The project uses GitHub Actions to automatically run tests on every pull request. Tests must pass before merging to main. The CI pipeline:

- Tests on macOS 12 (baseline) and latest
- Tests with Python 3.10
- Verifies the setup wizard runs correctly
- Runs all unit tests with coverage reporting

## Development Setup

If you want to contribute or modify the code:

### HDF5 Installation (for building from source)

When building from source, HDF5 is required for compiling the C++ extensions. The setup wizard will try to detect it automatically, but if it can't find it, you can install it via:

#### macOS

```bash
# Via Homebrew (recommended)
brew install hdf5

# Or via Conda
conda install -c conda-forge hdf5
```

#### Manual Installation

1. Download from https://github.com/HDFGroup/hdf5/releases
   - Choose the appropriate version for your OS
   - Download the tarball or zip file
2. Extract and install (you should now see an `hdf5` directory with `bin`, `include`, `lib`, etc.)
3. Set `HDF5_DIR` environment variable to the installation path

```bash
export HDF5_DIR=/path/to/hdf5
```

### Building the Package

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install in editable mode
pip install -e .
```

This can come in handy to view hdf5 files: [https://myhdf5.hdfgroup.org/](https://myhdf5.hdfgroup.org/)

## Troubleshooting

### "C++ extension not available"

If you installed via pip and see this error:
- Try reinstalling: `pip uninstall ysa-signal && pip install ysa-signal`
- Make sure you're using Python 3.6+: `python --version`

If you're building from source:
- Run the setup wizard: `python setup_wizard.py`
- Make sure HDF5 is installed
- Check that pybind11 is installed: `pip install pybind11`

### "Could not find HDF5 installation" (building from source only)

- Install HDF5 using one of the methods above
- Or set the `HDF5_DIR` environment variable: `export HDF5_DIR=/path/to/hdf5`
- Run the setup wizard again

### Compilation errors (building from source only)

- Make sure you have a C++ compiler installed (clang on macOS comes with Xcode Command Line Tools)
- Install Xcode Command Line Tools: `xcode-select --install`
- Check that Python development headers are installed
- Try updating pybind11: `pip install --upgrade pybind11`

### GUI doesn't launch

- Make sure tkinter is installed:
  - macOS (Homebrew): `brew install python-tk`
  - Conda: Should be included by default
  - Linux: `sudo apt-get install python3-tk`

## Version History

- **1.0.1**: Fixed C++ extension imports, added type stubs for better IDE support
- **1.0.0**: Initial PyPI release

## License

Copyright © 2025 Jake Cahoon

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/ParrishLab/ysa-signal/issues)
- Email: jacobbcahoon@gmail.com
- Text: (385) 307-9925
