from setuptools import setup, find_packages

setup(
    name="crypto_trading_simulator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'websockets',
        'requests',
    ],
) 