# Encoding: utf-8

# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os

from setuptools import setup, find_packages


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
    python_requires='>=2.7,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4',
    packages=find_packages(),
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=[
        "lxml"
        "@ https://files.pythonhosted.org/packages"
        "/06/5a/e11cad7b79f2cf3dd2ff8f81fa8ca667e7591d3d8451768589996b65dec1"
        "/lxml-4.9.2.tar.gz"
        " ; platform_system!='Windows' and python_full_version=='3.8.1'",
        "lxml ; platform_system=='Windows' or python_full_version!='3.8.1'",
    ],
)
