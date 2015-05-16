import os
import unittest
import doctest
import pkg_resources


def load_tests(loader, tests, ignore):
    dist = pkg_resources.get_distribution('aio.app')
    import pdb; pdb.set_trace()
    test_file = os.path.join(dist.location, 'README.rst')
    doctest.testfile(test_file, module_relative=False, optionflags=doctest.ELLIPSIS)
    return tests
