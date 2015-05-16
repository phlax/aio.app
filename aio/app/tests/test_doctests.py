import os
import unittest
import doctest
import pkg_resources


def load_tests(loader, tests, ignore):
    doctest.testfile(
        pkg_resources.resource_filename("aio.app", 'README.rst'),
        module_relative=False, optionflags=doctest.ELLIPSIS)
    return tests
