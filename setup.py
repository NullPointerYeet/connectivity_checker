from setuptools import setup, find_packages

setup(
    name="network-monitor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'ping3',
    ],
    author="Matija Mandic",
    author_email="matija.mandic@gmail.com",
    description="Network connectivity monitoring tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/matijamandic/network-monitor",
    classifiers=[
        "Programming Language :: Python :: 3.10 ",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)