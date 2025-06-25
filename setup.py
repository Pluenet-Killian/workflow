#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="ci_test",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ci_test=ci_test.cli:main',
        ],
    },
    description="Utilitaire CI pour projets C/C++",
    author="ChrisG-L",
    python_requires='>=3.6',
)
