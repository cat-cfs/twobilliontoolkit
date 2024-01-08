# setup.py
from setuptools import setup, find_packages

setup(
    name='SpatialTransformer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'git+https://github.com/cat-cfs/RippleUnzipple.git',
        # List your dependencies here if you have any
    ],
)