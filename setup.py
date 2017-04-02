#!/usr/bin/env python
from setuptools import setup, find_packages  # This setup relies on setuptools since distutils is insufficient and badly hacked code

version = '0.0.1'
author = 'David-Leon Pohl'
author_email = 'david-leon.pohl@rub.de'

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='hass_scripts',
    version=version,
    description='My collection of home assistant scripts.',
    url='https://github.com/DavidLP/hass_scripts',
    license='MIT License',
    author=author,
    maintainer=author,
    author_email=author_email,
    maintainer_email=author_email,
    packages=find_packages(),
    install_requires=required,
    include_package_data=True,  # accept all data files and directories matched by MANIFEST.in or found in source control
    package_data={'': ['README.*', 'VERSION'], 'docs': ['*'], 'examples': ['*']},
    platforms='linux'
)
