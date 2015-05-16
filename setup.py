"""
aio.app
"""
import sys
from setuptools import setup, find_packages

from aio.app import __version__ as version


install_requires = [
    'setuptools',
    "aio.signals",
    "aio.logging",
    "aio.config",
    "zope.dottedname"]

if sys.version_info < (3, 4):
    install_requires += ['asyncio']

tests_require = install_requires + ['aio.testing']

setup(
    name='aio.app',
    version=version,
    description="Aio application runner",
    classifiers=[
        "Programming Language :: Python 3.4",
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
    data_files=[
        ('', ['README.rst']),
        ('aio/app', ['tests/resources/*.conf']),
    ],
    zip_safe=False,
    tests_require=tests_require,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'aio = aio.app.management:main',
    ]})
