# -*- coding:utf-8 -*-
from setuptools import find_packages, setup

VERSION = '1.0.0'

setup(
    name="osc-boto",
    version=VERSION,
    packages=find_packages(exclude=['tests']),
    author='Outscale SAS',
    author_email='contact@outscale.com',
    description="Boto extension to use outscale specific API",
    url="http://www.outscale.com/",
    include_package_data=True,
    install_requires=[
        'setuptools',
        'boto==2.36.0',
    ],
)
