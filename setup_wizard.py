#!/usr/bin/env python3
"""
YSA Signal Setup Wizard

Interactive setup wizard to configure and build YSA Signal application.
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_macos_version():
    """Check if macOS version is compatible (10.0+)"""
    if sys.platform != 'darwin':
        return True  # Not macOS, skip check

    print_info("Checking macOS version...")
    try:
        import platform
        version_str = platform.mac_ver()[0]
        if version_str:
            major_version = int(version_str.split('.')[0])
            if major_version >= 10:
                print_success(f"macOS {version_str} detected (compatible)")
                return True
            else:
                print_error(f"macOS {version_str} detected. macOS 10.0 or higher is required.")
                print_error("Please upgrade your operating system to continue.")
                return False
        else:
            print_warning("Could not determine macOS version, continuing anyway...")
            return True
    except Exception as e:
        print_warning(f"Error checking macOS version: {e}")
        print_warning("Continuing anyway...")
        return True


def check_python_version():
    """Check if Python version is compatible"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print_success(
            f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(
            f"Python {version.major}.{version.minor} detected.")
        return False


def check_pip_package(package_name: str):
    """Check if a pip package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_pip_package(package_name: str):
    """Install a pip package"""
    print_info(f"Installing {package_name}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name])
        print_success(f"{package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to install {package_name}")
        return False


def check_and_install_dependencies():
    """Check and install required Python dependencies"""
    print_header("Checking Python Dependencies")

    required_packages = {
        'numpy': 'numpy',
        'h5py': 'h5py',
        'pybind11': 'pybind11',
    }

    all_installed = True
    for import_name, package_name in required_packages.items():
        print_info(f"Checking for {package_name}...")
        if check_pip_package(import_name):
            print_success(f"{package_name} is already installed")
        else:
            print_warning(f"{package_name} not found")
            if install_pip_package(package_name):
                pass
            else:
                all_installed = False

    return all_installed


def detect_hdf5():
    """Try to detect HDF5 installation"""
    print_header("Detecting HDF5 Installation")

    # Check environment variables
    for var in ['HDF5_DIR', 'HDF5_ROOT']:
        if var in os.environ:
            hdf5_path = os.environ[var]
            include_dir = os.path.join(hdf5_path, 'include')
            lib_dir = os.path.join(hdf5_path, 'lib')
            if os.path.isdir(include_dir) and os.path.isdir(lib_dir):
                print_success(f"Found HDF5 via ${var}: {hdf5_path}")
                return hdf5_path

    # Check conda environment
    if 'CONDA_PREFIX' in os.environ:
        conda_prefix = os.environ['CONDA_PREFIX']
        include_dir = os.path.join(conda_prefix, 'include')
        lib_dir = os.path.join(conda_prefix, 'lib')
        if os.path.isdir(include_dir) and os.path.isdir(lib_dir):
            # Check if HDF5 headers exist
            if os.path.exists(os.path.join(include_dir, 'H5Cpp.h')) or \
               os.path.exists(os.path.join(include_dir, 'hdf5', 'H5Cpp.h')):
                print_success(
                    f"Found HDF5 in conda environment: {conda_prefix}")
                return conda_prefix

    # Check Homebrew
    if sys.platform == 'darwin':
        try:
            hdf5_path = subprocess.check_output(
                ['brew', '--prefix', 'hdf5']).decode().strip()
            if os.path.isdir(hdf5_path):
                print_success(f"Found HDF5 via Homebrew: {hdf5_path}")
                return hdf5_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Check common system locations
    common_paths = []
    if sys.platform == 'darwin':
        common_paths = [
            '/opt/homebrew',
            '/usr/local',
            '/opt/local',
        ]
    elif sys.platform.startswith('linux'):
        common_paths = [
            '/usr',
            '/usr/local',
        ]

    for base_path in common_paths:
        include_dir = os.path.join(base_path, 'include')
        lib_dir = os.path.join(base_path, 'lib')
        if os.path.isdir(include_dir) and os.path.isdir(lib_dir):
            # Check if HDF5 headers exist
            if os.path.exists(os.path.join(include_dir, 'H5Cpp.h')) or \
               os.path.exists(os.path.join(include_dir, 'hdf5', 'H5Cpp.h')):
                print_success(f"Found HDF5 at: {base_path}")
                return base_path

    print_warning("Could not automatically detect HDF5 installation")
    return None


def guide_hdf5_installation():
    """Guide user through HDF5 installation"""
    print_header("HDF5 Installation Guide")

    print("HDF5 is required to process .brw/.h5 files.")
    print("\nYou have several options to install HDF5:\n")

    if sys.platform == 'darwin':
        print(
            f"{Colors.BOLD}Option 1: Install via Homebrew (Recommended for macOS){Colors.ENDC}")
        print("  Run: brew install hdf5")
        print()

        print(f"{Colors.BOLD}Option 2: Install via Conda{Colors.ENDC}")
        print("  Run: conda install -c conda-forge hdf5")
        print()

    print(f"{Colors.BOLD}Option: Download and Install Manually{Colors.ENDC}")
    print("  1. Download HDF5 from: https://www.hdfgroup.org/downloads/hdf5/")
    print("  2. Extract the archive")
    print("  3. Move the extracted folder to this directory (ysa-signal/)")
    print("  4. Set HDF5_DIR environment variable to point to the folder")
    print()

    choice = input(
        f"\n{Colors.BOLD}Have you installed HDF5? (yes/no): {Colors.ENDC}").strip().lower()

    if choice in ['yes', 'y']:
        # Try to detect again
        hdf5_path = detect_hdf5()
        if hdf5_path:
            return hdf5_path
        else:
            print_warning("Still unable to detect HDF5.")
            manual_path = input(
                f"{Colors.BOLD}Please enter the HDF5 installation path: {Colors.ENDC}").strip()
            if os.path.isdir(manual_path):
                return manual_path
            else:
                print_error(f"Invalid path: {manual_path}")
                return None
    else:
        print_info("Please install HDF5 and run this setup wizard again.")
        return None


def build_extensions(hdf5_path: str | None = None):
    """Build C++ extensions"""
    print_header("Building C++ Extensions")

    # Set HDF5_DIR if provided
    env = os.environ.copy()
    if hdf5_path:
        env['HDF5_DIR'] = hdf5_path
        print_info(f"Using HDF5_DIR: {hdf5_path}")

    # Change to extensions directory
    extensions_dir = os.path.join(os.path.dirname(__file__), 'extensions')

    print_info("Compiling C++ extensions...")
    print("This may take a few minutes...\n")

    try:
        # Run setup.py build
        result = subprocess.run(
            [sys.executable, 'setup.py', 'build_ext', '--inplace'],
            cwd=extensions_dir,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_success("C++ extensions compiled successfully!")

            # Check if .so/.pyd files were created
            so_files = list(Path(extensions_dir).glob('*.so')) + \
                list(Path(extensions_dir).glob('*.pyd'))
            if so_files:
                print_info("Created extension files:")
                for f in so_files:
                    print(f"  - {f.name}")
            return True
        else:
            print_error("Failed to compile C++ extensions")
            print("\nError output:")
            print(result.stderr)
            return False

    except Exception as e:
        print_error(f"Exception during compilation: {e}")
        return False


def verify_installation():
    """Verify that everything is installed correctly"""
    print_header("Verifying Installation")

    # Check if extensions can be imported
    extensions_dir = os.path.join(os.path.dirname(__file__), 'extensions')
    sys.path.insert(0, extensions_dir)

    try:
        import sz_se_detect
        print_success("sz_se_detect extension loaded successfully")

        import signal_analyzer
        print_success("signal_analyzer extension loaded successfully")

        # Try importing helper functions
        sys.path.insert(0, os.path.dirname(__file__))
        import helper_functions
        print_success("helper_functions module loaded successfully")

        if helper_functions.CPP_AVAILABLE:
            print_success("All components verified!")
            return True
        else:
            print_error("C++ extensions not available in helper_functions")
            return False

    except ImportError as e:
        print_error(f"Failed to import extensions: {e}")
        return False


def main():
    """Main setup wizard"""
    print_header("YSA Signal Setup Wizard")
    print("Welcome to YSA Signal! This wizard will help you set up the application.\n")

    # Check macOS version if on macOS
    if not check_macos_version():
        sys.exit(1)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check and install dependencies
    if not check_and_install_dependencies():
        print_error(
            "\nFailed to install dependencies. Please install them manually.")
        sys.exit(1)

    # Detect HDF5
    hdf5_path = detect_hdf5()

    if hdf5_path is None:
        hdf5_path = guide_hdf5_installation()
        if hdf5_path is None:
            print_error(
                "\nSetup incomplete. Please install HDF5 and run this wizard again.")
            sys.exit(1)

    # Build extensions
    if not build_extensions(hdf5_path):
        print_error(
            "\nFailed to build C++ extensions. Please check the error messages above.")
        sys.exit(1)

    # Verify installation
    if verify_installation():
        print_header("Setup Complete!")
        print_success("YSA Signal is ready to use!")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print("  1. Run the application: python ysa_signal.py")
        print("  2. Or use CLI mode: python ysa_signal.py input.brw output.h5")
        print()
        return 0
    else:
        print_error(
            "\nSetup completed but verification failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
