# setup.py
from setuptools import setup, find_packages

setup(
    name='twobilliontoolkit',
    version='1.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'dash==2.14.2',        
        'Fiona==1.9.4.post1',
        'geopandas==0.13.2',
        'matplotlib==3.7.2',
        'numpy==1.25.2',
        'pandas==2.2.2',
        'psycopg2==2.9.9',
        'py7zr==0.20.8',
        'PyQt5==5.15.10',
        'PyQt5_sip==12.13.0',
        'pywin32==306',
        'setuptools==68.2.2',
        'setuptools==57.4.0',
        'Shapely==2.0.4'
    ],
    extras_require={},
    package_data={
        'twobilliontoolkit.SpatialTransformer': ['database.ini']
    },
    python_requires=">=3.7"
)
