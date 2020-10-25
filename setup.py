#!/usr/bin/python

import setuptools

with open("./unbound_console/__init__.py", "r") as fh:
    for line in fh.read().splitlines():
        if line.startswith('__version__'):
            VERSION = line.split('"')[1]
            
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
    
KEYWORDS = ('unbound console control remote client')

setuptools.setup(
    name="unbound_console",
    version=VERSION,
    author="Denis MACHARD",
    author_email="d.machard@gmail.com",
    description="Python console for unbound",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/dmachard/unbound-console",
    packages=['unbound_console', 'tests'],
    include_package_data=True,
    platforms='any',
    keywords=KEYWORDS,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[
        "pyyaml"
    ]
)
