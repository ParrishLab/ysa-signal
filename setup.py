from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
import sys
import os
import subprocess


def get_hdf5_paths():
    """
    Dynamically find HDF5 installation paths.
    Priority: (1) HDF5_DIR/HDF5_ROOT, (2) active conda env, (3) Homebrew, (4) platform fallbacks.
    Returns: include_dir, library_dir, libraries, extra_link_args.
    """
    def pack(inc, lib, libs=None, extra=None):
        d = {
            "include_dir": inc,
            "library_dir": lib,
            "libraries": libs or ["hdf5", "hdf5_hl"],
            "extra_link_args": (extra or []) + (
                [f"-Wl,-rpath,{lib}"] if sys.platform == "darwin" else []
            ),
        }
        # Back-compat alias if other code still uses "lib_dir"
        d["lib_dir"] = d["library_dir"]
        return d

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
                return pack(inc, lib, libs=["hdf5_cpp", "hdf5"])

    # 2) Active conda environment
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        inc = os.path.join(conda_prefix, 'include')
        lib = os.path.join(conda_prefix, 'lib')
        if os.path.isdir(inc) and os.path.isdir(lib):
            print(f"Found HDF5 in conda environment: {conda_prefix}")
            return pack(inc, lib, libs=["hdf5_cpp", "hdf5"])

    # 3) Homebrew (works for both /opt/homebrew and /usr/local)
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
            return pack(inc, lib, libs=["hdf5_cpp", "hdf5"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 4) Existing platform fallbacks
    fallback_paths = {
        "darwin": {
            "include_dir": [
                "/opt/homebrew/include/hdf5",
                "/usr/local/include/hdf5",
                "/usr/include/hdf5",
                "/opt/homebrew/include",
                "/usr/local/include",
            ],
            "lib_dir": ["/opt/homebrew/lib", "/usr/local/lib", "/usr/lib"],
        },
        "win32": {
            "include_dir": [],
            "lib_dir": [],
        },
    }

    platform_paths = fallback_paths.get(sys.platform, {"include_dir": [], "lib_dir": []})
    include_dir = first_existing(platform_paths["include_dir"])
    lib_dir = first_existing(platform_paths["lib_dir"])

    if include_dir and lib_dir:
        print(f"Found HDF5 in system paths: include={include_dir}, lib={lib_dir}")
        return pack(include_dir, lib_dir, libs=["hdf5_cpp", "hdf5"])

    error_msg = "Could not find HDF5 installation. "
    if sys.platform == 'win32':
        error_msg += "On Windows, set HDF5_DIR environment variable."
    else:
        error_msg += (
            "Please install HDF5:\n"
            "  - macOS: brew install hdf5\n"
            "  - conda: conda install -c conda-forge hdf5"
        )
    raise RuntimeError(error_msg)


# Choose correct source file based on platform
if sys.platform == 'win32':
    sz_se_detect_source = 'extensions/sz_se_detect_win.cpp'
else:
    sz_se_detect_source = 'extensions/sz_se_detect.cpp'

# Determine compilation flags based on platform
extra_compile_flags = []
extra_link_flags = []

if sys.platform == 'win32':
    # MSVC compiler flags
    extra_compile_flags = ['/std:c++17', '/O2', '/EHsc', '/DH5_BUILT_AS_DYNAMIC_LIB']
    extra_link_flags = []
else:
    # GCC/Clang compiler flags (macOS/Linux)
    extra_compile_flags = ['-std=c++17', '-O3']
    extra_link_flags = []

    # Universal binary for macOS
    if sys.platform == 'darwin':
        extra_compile_flags.extend(['-arch', 'arm64', '-arch', 'x86_64'])
        extra_link_flags.extend(['-arch', 'arm64', '-arch', 'x86_64'])

# Only detect HDF5 when building wheels (not sdist)
# Check if we're in a build command that needs compilation
building_extension = any(arg in sys.argv for arg in ['build_ext', 'bdist_wheel', 'install', 'develop'])

if building_extension:
    print("=" * 70)
    print("Detecting HDF5 installation...")
    print("=" * 70)
    hdf5_paths = get_hdf5_paths()
    print("=" * 70)
    print(f"Using HDF5:")
    print(f"  Include: {hdf5_paths['include_dir']}")
    print(f"  Library: {hdf5_paths['library_dir']}")
    print("=" * 70)

    ext_modules = [
        Pybind11Extension(
            'sz_se_detect',
            [sz_se_detect_source],
            include_dirs=[
                pybind11.get_include(),
                hdf5_paths['include_dir'],
            ],
            library_dirs=[hdf5_paths['library_dir']],
            libraries=hdf5_paths['libraries'],
            extra_compile_args=extra_compile_flags + [f"-I{hdf5_paths['include_dir']}"] if sys.platform != 'win32' else extra_compile_flags + [f"/I{hdf5_paths['include_dir']}"],
            extra_link_args=extra_link_flags + hdf5_paths.get('extra_link_args', []) + ([f"-L{hdf5_paths['library_dir']}"] if sys.platform != 'win32' else [f"/LIBPATH:{hdf5_paths['library_dir']}"]),
        ),
        Pybind11Extension(
            'signal_analyzer',
            ['extensions/signal_analyzer.cpp'],
            include_dirs=[pybind11.get_include()],
            extra_compile_args=extra_compile_flags,
            extra_link_args=extra_link_flags,
        ),
    ]
else:
    # For sdist, just define extensions without HDF5 paths
    # They won't be compiled during sdist build
    ext_modules = [
        Pybind11Extension(
            'sz_se_detect',
            [sz_se_detect_source],
            include_dirs=[pybind11.get_include()],
            extra_compile_args=extra_compile_flags,
            extra_link_args=extra_link_flags,
        ),
        Pybind11Extension(
            'signal_analyzer',
            ['extensions/signal_analyzer.cpp'],
            include_dirs=[pybind11.get_include()],
            extra_compile_args=extra_compile_flags,
            extra_link_args=extra_link_flags,
        ),
    ]


# Minimal setup.py - metadata is in pyproject.toml
setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    py_modules=['ysa_signal', 'helper_functions', 'setup_wizard', '_version'],
    package_data={'': ['*.pyi', 'py.typed']},
)
