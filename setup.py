# setup.py
from setuptools import setup, find_packages

setup(
    name="network_monitor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'ping3'
    ]
)