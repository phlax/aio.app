import unittest
import doctest


def load_tests(loader, tests, ignore):
    app_folder = os.path.abspath(
        "%s/../../.." % os.path.dirname(__file__))
    
    tests.addTests(doctest.DocTestSuite(my_module_with_doctests))
    return tests
