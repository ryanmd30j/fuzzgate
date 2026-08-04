#!/usr/bin/env python3
import os
import sys
import shutil
import unittest

# Point sys.path to src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from target_select import compute_sha256, check_target_changed, update_target_status
from report_parser import parse_asan_log

class TestFuzzgate(unittest.TestCase):

    def setUp(self):
        """Set up temporary directory and mock binary for testing."""
        self.test_dir = ".test_tmp"
        self.cache_dir = os.path.join(self.test_dir, ".fuzz_cache")
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.mock_binary = os.path.join(self.test_dir, "mock_target")
        with open(self.mock_binary, "wb") as f:
            f.write(b"MOCK_BINARY_DATA_V1")

    def tearDown(self):
        """Clean up temporary test directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_sha256_computation(self):
        """Verify SHA-256 computation returns consistent hash."""
        hash_val = compute_sha256(self.mock_binary)
        self.assertIsNotNone(hash_val)
        self.assertEqual(len(hash_val), 64)

    def test_target_selection_skip_and_refuzz(self):
        """Verify R.5 selection skips unchanged PASSED binaries but re-fuzzes FAILED binaries."""
        # Initial check (New binary -> should return True)
        self.assertTrue(check_target_changed(self.mock_binary, self.cache_dir))
        
        # Mark target as PASSED
        update_target_status(self.mock_binary, passed=True, hash_cache_dir=self.cache_dir)
        
        # Check again (Unchanged & Passed -> should return False / SKIP)
        self.assertFalse(check_target_changed(self.mock_binary, self.cache_dir))

        # Mark target as FAILED
        update_target_status(self.mock_binary, passed=False, hash_cache_dir=self.cache_dir)

        # Check again (Unchanged & Failed -> should return True / RE-FUZZ)
        self.assertTrue(check_target_changed(self.mock_binary, self.cache_dir))

    def test_asan_report_parser(self):
        """Verify R.7 parser extracts heap-buffer-overflow from raw ASan stderr."""
        mock_asan_log = """
        ==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000007a
        READ of size 1 at 0x60200000007a thread T0
            #0 0x5590ab2fc840 in LLVMFuzzerTestOneInput /fuzzgate/examples/vulnerable_target/target.cpp:9:17
        SUMMARY: AddressSanitizer: heap-buffer-overflow /fuzzgate/examples/vulnerable_target/target.cpp:9:17
        """
        report = parse_asan_log(mock_asan_log, "vulnerable_target")
        self.assertIn("heap-buffer-overflow", report)
        self.assertIn("vulnerable_target", report)
        self.assertIn("LLVMFuzzerTestOneInput", report)

if __name__ == "__main__":
    unittest.main()