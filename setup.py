#! /usr/bin/env python3
"""Installations script."""


from setuptools import setup


setup(
    name='digsigclt',
    version_format='{tag}',
    setup_requires=['setuptools-git-version'],
    python_requires='>=3.4',
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info@homeinfo.de>',
    maintainer='Richard Neumann',
    maintainer_email='<r.neumann@homeinfo.de>',
    packages=['digsigclt'],
    scripts=['files/digsigclt'],
    description=('Digital signage data synchronization client.')
)
