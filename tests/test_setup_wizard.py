#!/usr/bin/env python3
"""
Unit tests for setup_wizard.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup_wizard import (
    check_python_version,
    check_macos_version,
    check_pip_package,
)


class TestCheckPythonVersion(unittest.TestCase):
    """Test check_python_version function"""

    def test_current_python_version(self):
        """Test that current Python version passes check"""
        # Since we're running this test, the version should be compatible
        result = check_python_version()
        self.assertTrue(result)

    @patch('sys.version_info')
    def test_old_python_version(self, mock_version):
        """Test that old Python versions fail check"""
        mock_version.major = 2
        mock_version.minor = 7
        mock_version.micro = 18

        result = check_python_version()
        self.assertFalse(result)

    @patch('sys.version_info')
    def test_minimum_python_version(self, mock_version):
        """Test that Python 3.6 passes check"""
        mock_version.major = 3
        mock_version.minor = 6
        mock_version.micro = 0

        result = check_python_version()
        self.assertTrue(result)


class TestCheckMacOSVersion(unittest.TestCase):
    """Test check_macos_version function"""

    @patch('sys.platform', 'linux')
    def test_non_macos_platform(self):
        """Test that non-macOS platforms pass the check"""
        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_12_compatible(self, mock_mac_ver):
        """Test that macOS 12+ passes the check"""
        mock_mac_ver.return_value = ('12.0.0', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_13_compatible(self, mock_mac_ver):
        """Test that macOS 13+ passes the check"""
        mock_mac_ver.return_value = ('13.5.1', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_14_compatible(self, mock_mac_ver):
        """Test that macOS 14+ passes the check"""
        mock_mac_ver.return_value = ('14.0', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_11_compatible(self, mock_mac_ver):
        """Test that macOS 11 passes the check"""
        mock_mac_ver.return_value = ('11.7.0', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_10_compatible(self, mock_mac_ver):
        """Test that macOS 10 passes the check"""
        mock_mac_ver.return_value = ('10.15.7', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_9_incompatible(self, mock_mac_ver):
        """Test that macOS 9 and below fails the check"""
        mock_mac_ver.return_value = ('9.2.2', ('', '', ''), '')

        result = check_macos_version()
        self.assertFalse(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_unknown_macos_version(self, mock_mac_ver):
        """Test that unknown version returns True with warning"""
        mock_mac_ver.return_value = ('', ('', '', ''), '')

        result = check_macos_version()
        self.assertTrue(result)

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_macos_version_check_exception(self, mock_mac_ver):
        """Test that exceptions during version check are handled gracefully"""
        mock_mac_ver.side_effect = Exception("Test exception")

        result = check_macos_version()
        self.assertTrue(result)  # Should continue with warning


class TestCheckPipPackage(unittest.TestCase):
    """Test check_pip_package function"""

    def test_check_existing_package(self):
        """Test checking for a package that exists (sys)"""
        result = check_pip_package('sys')
        self.assertTrue(result)

    def test_check_nonexistent_package(self):
        """Test checking for a package that doesn't exist"""
        result = check_pip_package('nonexistent_package_xyz123')
        self.assertFalse(result)

    def test_check_numpy(self):
        """Test checking for numpy (should be installed)"""
        result = check_pip_package('numpy')
        self.assertTrue(result)


class TestSetupWizardIntegration(unittest.TestCase):
    """Integration tests for setup wizard"""

    def test_system_compatibility(self):
        """Test that the current system passes basic compatibility checks"""
        # Python version should pass
        self.assertTrue(check_python_version())

        # macOS version should pass (or we're not on macOS)
        self.assertTrue(check_macos_version())

    @patch('sys.platform', 'darwin')
    @patch('platform.mac_ver')
    def test_full_compatibility_check_sequence(self, mock_mac_ver):
        """Test the full sequence of compatibility checks"""
        mock_mac_ver.return_value = ('13.0', ('', '', ''), '')

        # Run all checks
        python_ok = check_python_version()
        macos_ok = check_macos_version()

        self.assertTrue(python_ok)
        self.assertTrue(macos_ok)


if __name__ == '__main__':
    unittest.main()
