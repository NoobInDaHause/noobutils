from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

__version__ = "1.1.8"

setup(
    name="noobutils",
    version=__version__,
    description="Various shared utils and shit for my NoobCogs.",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NoobInDaHause/noobutils",
    author="NoobInDaHause",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires=">=3.10",
)
