"""
aio.app
"""
from setuptools import setup, find_packages

from aio.app import __version__ as version


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
    zip_safe=False,
    tests_require=["aio.testing"],
    install_requires=['setuptools', "asyncio"],
    entry_points="""
    # -*- Entry points: -*-
    """)
