from setuptools import setup, find_packages

setup(
    name="sis-drones",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'networkx',
        'matplotlib',
    ],
) 