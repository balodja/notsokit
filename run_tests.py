#!/usr/bin/env python
"""Simple test runner for notsokit."""

import sys
import unittest

if __name__ == '__main__':
	# Discover and run all tests in notsokit/test/
	loader = unittest.TestLoader()
	suite = loader.discover('notsokit/test', pattern='test_*.py')
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	sys.exit(0 if result.wasSuccessful() else 1)
