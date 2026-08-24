from setuptools import setup, find_packages

setup(
    name="quilt-bathy",
    version="0.1.0",
    description="The bathy cross-section as a working tool. The substrate, applied to the sailor's actual use case. The Inner Sound, as a cell-graph.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="SuperInstance",
    license="MIT",
    py_modules=["bathy"],
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=["quilt-substrate"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    entry_points={
        "console_scripts": [
            "quilt-bathy=bathy:_cli",
        ],
    },
)
