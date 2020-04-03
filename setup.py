# Encoding: utf-8

# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import sys
import subprocess

from setuptools import setup, find_packages

try:
    import stackless  # noqa: F401

    # Under Stackless Python or PyPy, the pre-compiled lxml wheel ends with a segfault
    subprocess.check_call([sys.executable] + ' -m pip install --no-binary :all: lxml'.split())
    install_requires = []
except ImportError:
    install_requires = ['lxml']

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as description:
    LONG_DESCRIPTION = description.read()

setup(
    name='nagare-renderers-xml',
    author='Net-ng',
    author_email='alain.poirier@net-ng.com',
    description='Nagare XML renderer',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='',
    url='https://github.com/nagareproject/renderers-xml',
    python_requires='>=2.7.*,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4',
    packages=find_packages(),
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=install_requires
)
