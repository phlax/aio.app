"""
aio.app
"""
import os
import sys
from setuptools import setup, find_packages

version = "0.0.29"

install_requires = [
    "distribute",
    "aio.signals",
    "aio.config",
    "zope.dottedname"]

if sys.version_info < (3, 4):
    install_requires += ['asyncio']

tests_require = install_requires + ['aio.testing>=0.2']


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    'Detailed documentation\n'
    + '**********************\n'
    + '\n'
    + read("README.rst")
    + '\n')

try:
    long_description += (
        '\n'
        + read("aio", "app", "README.rst")
        + '\n')
except FileNotFoundError:
    pass

setup(
    name='aio.app',
    version=version,
    description="Aio application runner",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='',
    author='Ryan Northey',
    author_email='ryan@3ca.org.uk',
    url='http://github.com/phlax/aio.app',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['aio'],
    include_package_data=True,
    zip_safe=False,
    tests_require=tests_require,
    test_suite="aio.app.tests",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'aio = aio.app.management:main']})
