from setuptools import find_packages, setup

setup(
    name="crypto-arbitrage-monitor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.110.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.8",
        "uvicorn>=0.23",
    ],
)
