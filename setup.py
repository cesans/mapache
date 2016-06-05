#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    test_requirements = f.read().splitlines()

setup(
    name='mapache',
    version='0.1.0',
    description="An early-stage work-in-progress library for the analysis and visualization of opinion polls and other electoral data.",
    long_description=readme + '\n\n',
    author="Carlos Sanchez",
    author_email='cesanxz@gmail.com',
    url='https://github.com/cesans/mapache',
    packages=[
        'mapache',
    ],
    package_dir={'mapache':
                 'mapache'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='mapache',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
