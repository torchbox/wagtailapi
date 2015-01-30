#!/usr/bin/env python

import sys, os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Hack to prevent "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when setup.py exits
# (see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass


from wagtailapi import __version__


setup(
    name='wagtailapi',
    version=__version__,
    description='A module for adding a read only, JSON based web API to your Wagtail site',
    author='Karl Hobley',
    author_email='karlhobley10@gmail.com',
    url='https://github.com/torchbox/wagtailapi',
    packages=['wagtailapi'],
    include_package_data=True,
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'wagtail>=0.8',
    ],
    zip_safe=False,
)

