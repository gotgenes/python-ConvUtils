#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

import re
import os

VERSIONFILE = os.path.sep.join(('convutils', '_version.py'))
VERSTRLINE = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
MATCH = re.search(VSRE, VERSTRLINE, re.M)
if MATCH:
    VERSTR = MATCH.group(1)
else:
    raise RuntimeError(
            "Unable to find version string in " "{0}.".format(
                    VERSIONFILE)
    )

setup(
    name='ConvUtils',
    version=VERSTR,
    author='Christopher D. Lasher',
    author_email='chris.lasher@gmail.com',
    packages=['convutils', 'convutils.tests'],
    url='http://pypi.python.org/pypi/ConvUtils/',
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
    description=("A library of convenient utility functions and pure "
        "Python data structures."),
    long_description=open('README.rst').read(),
)

