# setup.py
from setuptools import setup, find_packages

setup(
    name='twobilliontoolkit',
    version='1.0',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'dash==2.14.2',
        'pandas==2.1.4',
        'psycopg2==2.9.9',
        'py7zr==0.20.8',
        'pywin32==306',
        'setuptools==68.2.2'
    ],
    extras_require={},
    package_data={},
    python_requires=">=3.7"
)
