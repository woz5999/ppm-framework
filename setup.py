from setuptools import setup, find_packages

setup(
    name="ppm-framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy>=1.24.0", "scipy>=1.11.0", "matplotlib>=3.7.0"],
    python_requires=">=3.9",
    description="PPM Framework — Deriving Physical Constants from Z2 → RP3 Topology",
    author="PPM Framework Authors",
    license="MIT",
)
