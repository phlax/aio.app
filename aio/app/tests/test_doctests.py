import os
import unittest
import doctest
import pkg_resources


def load_tests(loader, tests, ignore):
    dist = pkg_resources.get_distribution('aio.app')
    test_file = os.path.join(dist.location, 'README.rst')
    doctest.testfile(test_file, module_relative=False)
    return tests
