#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

setup(
    name='orb_api',
    version='0.1.0',
    description='Python wrapper for ORB API',
    long_description=readme,
    packages=[
        'orb_api',
    ],
    include_package_data=True,
    install_requires=[
        'requests>=2.0.0',
        'poster==0.8.1',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',  # provisional
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='tests',
)
