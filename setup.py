from setuptools import setup

setup(
    name='sourcearena-py',
    version='1.0',
    description='An async client for using sourcearena api',
    author='apri-me',
    packages=['sourcearenapy'],
    install_requires=[
        'aiohttp',
    ],
)