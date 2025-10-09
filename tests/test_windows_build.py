#!/usr/bin/env python3
"""
Unit tests for Windows build configuration and extensions
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWindowsSetupConfiguration(unittest.TestCase):
    """Test Windows-specific setup configuration"""

    def setUp(self):
        """Set up test environment"""
        self.original_environ = os.environ.copy()
        self.test_workspace = tempfile.mkdtemp()
        os.environ["GITHUB_WORKSPACE"] = self.test_workspace

    def tearDown(self):
        """Clean up test environment"""
        os.environ.clear()
        os.environ.update(self.original_environ)
        if os.path.exists(self.test_workspace):
            os.rmdir(self.test_workspace)

    def test_hdf5_paths_configuration(self):
        """Test HDF5 paths are correctly configured from environment"""
        # Import the setup module (we'll check its configuration)
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )

        # Verify win_setup.py exists
        win_setup_path = os.path.join(extensions_dir, "win_setup.py")
        self.assertTrue(
            os.path.exists(win_setup_path),
            f"Windows setup file should exist at {win_setup_path}"
        )

        # Read and verify key configuration elements
        with open(win_setup_path, 'r') as f:
            setup_content = f.read()

        # Check for essential MSVC compiler flags
        self.assertIn("/std:c++17", setup_content,
                      "Should use MSVC C++17 flag")
        self.assertIn("H5_BUILT_AS_DYNAMIC_LIB", setup_content,
                      "Should define H5_BUILT_AS_DYNAMIC_LIB for dynamic linking")

        # Check for HDF5 library configuration
        self.assertIn("hdf5_cpp", setup_content,
                      "Should link against hdf5_cpp library")
        self.assertIn("hdf5", setup_content,
                      "Should link against hdf5 library")

        # Check for both modules
        self.assertIn("sz_se_detect", setup_content,
                      "Should configure sz_se_detect extension")
        self.assertIn("signal_analyzer", setup_content,
                      "Should configure signal_analyzer extension")

    def test_windows_cpp_file_exists(self):
        """Test Windows-specific C++ source file exists"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        self.assertTrue(
            os.path.exists(win_cpp_path),
            f"Windows C++ source should exist at {win_cpp_path}"
        )

    def test_windows_specific_headers(self):
        """Test Windows C++ file uses correct Windows-specific headers"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            cpp_content = f.read()

        # Check for Windows-specific includes
        self.assertIn("<direct.h>", cpp_content,
                      "Should include direct.h for Windows")
        self.assertIn("_getcwd", cpp_content,
                      "Should use _getcwd for Windows")

        # Check that it doesn't use Unix-specific headers
        self.assertNotIn("<pwd.h>", cpp_content,
                         "Should not include pwd.h (Unix-specific)")
        self.assertNotIn("getpwuid", cpp_content,
                         "Should not use getpwuid (Unix-specific)")

        # Check for USERPROFILE (Windows home directory)
        self.assertIn("USERPROFILE", cpp_content,
                      "Should use USERPROFILE environment variable")

    def test_compiler_flags_msvc(self):
        """Test MSVC-specific compiler flags in setup"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_setup_path = os.path.join(extensions_dir, "win_setup.py")

        if not os.path.exists(win_setup_path):
            self.skipTest("Windows setup file not found")

        with open(win_setup_path, 'r') as f:
            setup_content = f.read()

        # Check MSVC flags (not GCC/Clang flags)
        self.assertIn("/std:c++17", setup_content,
                      "Should use /std:c++17 (MSVC flag)")
        self.assertNotIn("-std=c++17", setup_content,
                         "Should not use -std=c++17 (GCC/Clang flag) in Windows setup")

        # Check for LIBPATH (MSVC) not -L (GCC/Clang)
        self.assertIn("/LIBPATH:", setup_content,
                      "Should use /LIBPATH: for library paths")


class TestWindowsExtensionFunctionality(unittest.TestCase):
    """Test that Windows extensions maintain the same functionality as macOS"""

    def test_core_detection_algorithm_present(self):
        """Test that core detection algorithms are present in Windows version"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")
        mac_cpp_path = os.path.join(extensions_dir, "sz_se_detect.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")
        if not os.path.exists(mac_cpp_path):
            self.skipTest("macOS C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            win_content = f.read()
        with open(mac_cpp_path, 'r') as f:
            mac_content = f.read()

        # Check for key functions that should be identical
        key_functions = [
            "SzSEDetectLEGIT",
            "findpeaks",
            "movvar",
            "getChs",
            "get_cat_envelop",
            "processAllChannels",
        ]

        for func_name in key_functions:
            self.assertIn(func_name, win_content,
                          f"Function {func_name} should be present in Windows version")
            self.assertIn(func_name, mac_content,
                          f"Function {func_name} should be present in macOS version")

    def test_detection_structs_match(self):
        """Test that data structures are the same in both versions"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")
        mac_cpp_path = os.path.join(extensions_dir, "sz_se_detect.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")
        if not os.path.exists(mac_cpp_path):
            self.skipTest("macOS C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            win_content = f.read()
        with open(mac_cpp_path, 'r') as f:
            mac_content = f.read()

        # Check for key data structures
        key_structs = [
            "struct ChannelData",
            "struct DetectionResult",
            "struct ChannelDetectionResult",
            "struct ElectrodeInfo",
        ]

        for struct_name in key_structs:
            self.assertIn(struct_name, win_content,
                          f"Struct {struct_name} should be in Windows version")
            self.assertIn(struct_name, mac_content,
                          f"Struct {struct_name} should be in macOS version")

    def test_pybind11_module_definition(self):
        """Test that Python bindings are correctly defined"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            content = f.read()

        # Check for pybind11 module definition
        self.assertIn("PYBIND11_MODULE(sz_se_detect, m)", content,
                      "Should define pybind11 module for sz_se_detect")

        # Check that key classes are exposed to Python
        self.assertIn("py::class_<DetectionResult>", content,
                      "Should expose DetectionResult to Python")
        self.assertIn("py::class_<ChannelDetectionResult>", content,
                      "Should expose ChannelDetectionResult to Python")

        # Check that main function is exposed
        self.assertIn('m.def("processAllChannels"', content,
                      "Should expose processAllChannels function to Python")

    def test_hdf5_version_compatibility(self):
        """Test that HDF5 version compatibility is handled"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            content = f.read()

        # Check for HDF5 includes
        self.assertIn("#include \"H5Cpp.h\"", content,
                      "Should include HDF5 C++ header")

        # Check for H5O_info2_t usage (HDF5 1.12+)
        self.assertIn("H5O_info2_t", content,
                      "Should use H5O_info2_t for HDF5 compatibility")


class TestSignalAnalyzerConsistency(unittest.TestCase):
    """Test that signal_analyzer.cpp is consistent across platforms"""

    def test_signal_analyzer_platform_independent(self):
        """Test that signal_analyzer doesn't need platform-specific code"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        signal_analyzer_path = os.path.join(extensions_dir, "signal_analyzer.cpp")

        if not os.path.exists(signal_analyzer_path):
            self.skipTest("signal_analyzer.cpp not found")

        with open(signal_analyzer_path, 'r') as f:
            content = f.read()

        # signal_analyzer should not have platform-specific code
        self.assertNotIn("<pwd.h>", content,
                         "signal_analyzer should not use Unix-specific headers")
        self.assertNotIn("<direct.h>", content,
                         "signal_analyzer should not use Windows-specific headers")
        self.assertNotIn("getenv", content,
                         "signal_analyzer should not access environment variables")

        # Should have pybind11 module
        self.assertIn("PYBIND11_MODULE(signal_analyzer, m)", content,
                      "Should define pybind11 module")

    def test_signal_analyzer_in_win_setup(self):
        """Test that signal_analyzer is included in Windows setup"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_setup_path = os.path.join(extensions_dir, "win_setup.py")

        if not os.path.exists(win_setup_path):
            self.skipTest("Windows setup file not found")

        with open(win_setup_path, 'r') as f:
            content = f.read()

        # Should build signal_analyzer with MSVC flags
        self.assertIn('"signal_analyzer"', content,
                      "Should include signal_analyzer in extensions")
        self.assertIn('["signal_analyzer.cpp"]', content,
                      "Should reference signal_analyzer.cpp source")


class TestPathExpansionConsistency(unittest.TestCase):
    """Test that path expansion works correctly on Windows"""

    def test_expandTilde_function_present(self):
        """Test that expandTilde function exists in Windows version"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            content = f.read()

        # Check for expandTilde function
        self.assertIn("std::string expandTilde", content,
                      "Should have expandTilde function")

        # Check that it uses Windows-appropriate methods
        self.assertIn("USERPROFILE", content,
                      "Should use USERPROFILE for home directory")

    def test_path_handling_consistency(self):
        """Test that file path handling is present in both versions"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")
        mac_cpp_path = os.path.join(extensions_dir, "sz_se_detect.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")
        if not os.path.exists(mac_cpp_path):
            self.skipTest("macOS C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            win_content = f.read()
        with open(mac_cpp_path, 'r') as f:
            mac_content = f.read()

        # Both should have createFilePath function
        self.assertIn("createFilePath", win_content,
                      "Windows version should have createFilePath")
        self.assertIn("createFilePath", mac_content,
                      "macOS version should have createFilePath")


class TestThreadingSupport(unittest.TestCase):
    """Test that multithreading support is consistent"""

    def test_threading_in_windows_version(self):
        """Test that Windows version includes threading support"""
        extensions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "extensions"
        )
        win_cpp_path = os.path.join(extensions_dir, "sz_se_detect_win.cpp")

        if not os.path.exists(win_cpp_path):
            self.skipTest("Windows C++ source file not found")

        with open(win_cpp_path, 'r') as f:
            content = f.read()

        # Check for threading support
        self.assertIn("#include <thread>", content,
                      "Should include thread header")
        self.assertIn("#include <mutex>", content,
                      "Should include mutex header")
        self.assertIn("#include <atomic>", content,
                      "Should include atomic header")

        # Check for GIL handling
        self.assertIn("py::gil_scoped_release", content,
                      "Should release GIL for multithreaded processing")
        self.assertIn("py::gil_scoped_acquire", content,
                      "Should reacquire GIL when needed")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
