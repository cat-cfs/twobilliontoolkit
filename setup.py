# setup.py
from setuptools import setup, find_packages
import platform

requirements = [
    'Fiona==1.9.4.post1',
    'geopandas==0.13.2',
    'pandas==2.2.2',
    'psycopg2==2.9.9',
    'py7zr==0.20.8',
    'PyQt5==5.15.10',
    'PyQt5_sip==12.13.0',
    'setuptools==68.2.2',
    'mkdocs==1.6.0',
    'mkdocstrings==0.25.1',
    'mkdocs-material==9.5.28',
    'dash==2.14.2'
]

# Add pywin32 only if running on Windows
if platform.system() == "Windows":
    requirements.append('pywin32==306')
    
setup(
    name='twobilliontoolkit',
    version='1.4',
    packages=find_packages(exclude=['ArcGISAddin', 'ArcGISToolbox', 'tests']),
    install_requires=requirements,
    extras_require={},
    package_data={
        'twobilliontoolkit.SpatialTransformer': ['database.ini']
    },
    python_requires=">=3.7"
)
