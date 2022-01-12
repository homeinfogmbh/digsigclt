#! /usr/bin/env python3
"""Installations script."""

from setuptools import setup


setup(
    name='digsigclt',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    python_requires='>=3.8',
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info@homeinfo.de>',
    maintainer='Richard Neumann',
    maintainer_email='<r.neumann@homeinfo.de>',
    packages=[
        'digsigclt',
        'digsigclt.os',
        'digsigclt.os.posix',
        'digsigclt.rpc'
    ],
    install_requires=['netifaces'],
    entry_points={'console_scripts': ['digsigclt = digsigclt:main']},
    description=('Digital signage data synchronization client.')
)
