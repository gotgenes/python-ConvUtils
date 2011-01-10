#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='ConvUtils',
    version='1.0',
    author='Christopher D. Lasher',
    author_email='chris.lasher@gmail.com',
    packages=['convutils', 'convutils.test'],
    url='http://pypi.python.org/pypi/ConvUtils/',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries'
    ],
    description=("A library of convenient utility functions and pure "
        "Python data structures"),
    long_description=open('README.txt').read(),
)

