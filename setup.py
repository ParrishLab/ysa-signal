from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess


class get_pybind_include:
    """Helper class to determine the pybind11 include path"""
    def __str__(self):
        import pybind11
        return pybind11.get_include()


def get_h5py_hdf5_paths():
    """
    Get HDF5 paths from h5py installation.
    This uses the HDF5 library that h5py was built against.
    """
    try:
        import h5py
        import os

        # Get h5py installation directory
        h5py_dir = os.path.dirname(h5py.__file__)

        # Try to get HDF5 paths from h5py config
        hdf5_version = h5py.version.hdf5_version
        print(f"Found h5py with HDF5 version: {hdf5_version}")

        # Get the library directory from h5py
        # h5py typically includes the HDF5 libraries it was built against
        h5py_lib_dir = os.path.join(h5py_dir, '.dylibs')  # macOS

        # Check various possible locations for h5py's HDF5
        possible_lib_dirs = [
            h5py_lib_dir,
            os.path.join(h5py_dir, 'lib'),
            os.path.join(os.path.dirname(h5py_dir), 'lib'),
        ]

        # If h5py was installed via conda, check conda prefix
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            possible_lib_dirs.extend([
                os.path.join(conda_prefix, 'lib'),
            ])

        # Check if h5py was built against system HDF5
        for lib_dir in possible_lib_dirs:
            if os.path.isdir(lib_dir):
                # Check if HDF5 libraries exist
                hdf5_lib_exists = any(
                    f.startswith('libhdf5') for f in os.listdir(lib_dir)
                ) if os.path.exists(lib_dir) else False

                if hdf5_lib_exists:
                    print(f"Found HDF5 libraries in: {lib_dir}")

                    # Find include directory
                    possible_inc_dirs = [
                        os.path.join(os.path.dirname(lib_dir), 'include'),
                        os.path.join(os.path.dirname(os.path.dirname(lib_dir)), 'include'),
                    ]

                    for inc_dir in possible_inc_dirs:
                        h5_inc = os.path.join(inc_dir, 'hdf5')
                        if os.path.isdir(h5_inc):
                            inc_dir = h5_inc
                        if os.path.isdir(inc_dir) and os.path.exists(os.path.join(inc_dir, 'H5Cpp.h')):
                            print(f"Found HDF5 headers in: {inc_dir}")
                            return {
                                'include_dir': inc_dir,
                                'library_dir': lib_dir,
                                'libraries': ['hdf5_cpp', 'hdf5'],
                            }

        # Fall back to system HDF5 paths
        print("Could not find HDF5 in h5py installation, trying system paths...")
        return get_system_hdf5_paths()

    except ImportError:
        raise RuntimeError(
            "h5py is required but not installed. "
            "Please install it with: pip install h5py"
        )
    except Exception as e:
        print(f"Warning: Could not determine h5py HDF5 paths: {e}")
        print("Falling back to system HDF5 detection...")
        return get_system_hdf5_paths()


def get_system_hdf5_paths():
    """
    Fallback: Try to find HDF5 in system locations.
    Priority: (1) HDF5_DIR/HDF5_ROOT, (2) conda env, (3) Homebrew, (4) system paths
    """
    def first_existing(paths):
        for p in paths:
            if os.path.isdir(p):
                return p
        return None

    # 1) HDF5_DIR / HDF5_ROOT environment variables
    for var in ('HDF5_DIR', 'HDF5_ROOT'):
        base = os.environ.get(var)
        if base:
            inc = os.path.join(base, 'include')
            lib = os.path.join(base, 'lib')
            if os.path.isdir(inc) and os.path.isdir(lib):
                print(f"Found HDF5 via {var}: {base}")
                return {
                    'include_dir': inc,
                    'library_dir': lib,
                    'libraries': ['hdf5_cpp', 'hdf5'],
                }

    # 2) Active conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        inc = os.path.join(conda_prefix, 'include')
        lib = os.path.join(conda_prefix, 'lib')
        if os.path.isdir(inc) and os.path.isdir(lib):
            # Check if HDF5 actually exists
            if os.path.exists(os.path.join(inc, 'H5Cpp.h')):
                print(f"Found HDF5 in conda environment: {conda_prefix}")
                return {
                    'include_dir': inc,
                    'library_dir': lib,
                    'libraries': ['hdf5_cpp', 'hdf5'],
                }

    # 3) Homebrew
    try:
        prefix = subprocess.check_output(['brew', '--prefix', 'hdf5'],
                                        stderr=subprocess.DEVNULL).decode().strip()
        inc = first_existing([
            os.path.join(prefix, 'include', 'hdf5'),
            os.path.join(prefix, 'include')
        ])
        lib = os.path.join(prefix, 'lib')
        if inc and os.path.isdir(lib):
            print(f"Found HDF5 via Homebrew: {prefix}")
            return {
                'include_dir': inc,
                'library_dir': lib,
                'libraries': ['hdf5_cpp', 'hdf5'],
            }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 4) System paths
    if sys.platform == 'darwin':
        inc_paths = [
            '/opt/homebrew/include/hdf5',
            '/opt/homebrew/include',
            '/usr/local/include/hdf5',
            '/usr/local/include',
        ]
        lib_paths = [
            '/opt/homebrew/lib',
            '/usr/local/lib',
        ]
    else:  # Linux
        inc_paths = [
            '/usr/include/hdf5/serial',
            '/usr/local/include/hdf5',
            '/usr/include/hdf5',
            '/usr/include',
        ]
        lib_paths = [
            '/usr/lib/x86_64-linux-gnu',
            '/usr/local/lib',
            '/usr/lib',
        ]

    inc = first_existing(inc_paths)
    lib = first_existing(lib_paths)

    if inc and lib:
        print(f"Found HDF5 in system paths: include={inc}, lib={lib}")
        return {
            'include_dir': inc,
            'library_dir': lib,
            'libraries': ['hdf5_cpp', 'hdf5'],
        }

    raise RuntimeError(
        "Could not find HDF5 installation. "
        "Please install h5py (which includes HDF5): pip install h5py\n"
        "Or install HDF5 separately:\n"
        "  - macOS: brew install hdf5\n"
        "  - Linux: sudo apt-get install libhdf5-dev\n"
        "  - conda: conda install -c conda-forge hdf5"
    )


class BuildExt(build_ext):
    """Custom build extension to add platform-specific options"""

    def build_extensions(self):
        # Determine compilation flags based on platform
        extra_compile_args = ['-std=c++17', '-O3']
        extra_link_args = []

        # Universal binary for macOS
        if sys.platform == 'darwin':
            extra_compile_args.extend(['-arch', 'arm64', '-arch', 'x86_64'])
            extra_link_args.extend(['-arch', 'arm64', '-arch', 'x86_64'])

        # Add flags to all extensions
        for ext in self.extensions:
            ext.extra_compile_args.extend(extra_compile_args)
            ext.extra_link_args.extend(extra_link_args)

            # Add rpath on macOS for HDF5 library
            if sys.platform == 'darwin':
                for lib_dir in ext.library_dirs:
                    ext.extra_link_args.append(f'-Wl,-rpath,{lib_dir}')

        build_ext.build_extensions(self)


# Get HDF5 paths from h5py or system
print("=" * 70)
print("Detecting HDF5 installation...")
print("=" * 70)
hdf5_paths = get_h5py_hdf5_paths()
print("=" * 70)
print(f"Using HDF5:")
print(f"  Include: {hdf5_paths['include_dir']}")
print(f"  Library: {hdf5_paths['library_dir']}")
print("=" * 70)


ext_modules = [
    Extension(
        'sz_se_detect',
        sources=['extensions/sz_se_detect.cpp'],
        include_dirs=[
            get_pybind_include(),
            hdf5_paths['include_dir'],
        ],
        library_dirs=[hdf5_paths['library_dir']],
        libraries=hdf5_paths['libraries'],
        extra_compile_args=[f"-I{hdf5_paths['include_dir']}"],
        extra_link_args=[f"-L{hdf5_paths['library_dir']}"],
        language='c++',
    ),
    Extension(
        'signal_analyzer',
        sources=['extensions/signal_analyzer.cpp'],
        include_dirs=[get_pybind_include()],
        extra_compile_args=[],
        extra_link_args=[],
        language='c++',
    ),
]


# Read the long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ysa-signal',
    version='1.0.12',
    author='Jake Cahoon',
    author_email='jacobbcahoon@gmail.com',
    description='YSA Signal - Standalone signal analyzer for .brw/.h5 files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ParrishLab/ysa-signal',
    py_modules=['ysa_signal', 'helper_functions', 'setup_wizard'],
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt},
    data_files=[('', ['ysa_signal.pyi', 'helper_functions.pyi', 'setup_wizard.pyi', 'py.typed'])],
    install_requires=[
        'numpy>=1.19.0',
        'h5py>=3.0.0',
        'pybind11>=2.6.0',
        'matplotlib>=3.3.0',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ysa-signal=ysa_signal:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: C++',
        'Operating System :: MacOS :: MacOS X',
    ],
    keywords='signal processing, neuroscience, electrophysiology, MEA, seizure detection',
    zip_safe=False,
)
